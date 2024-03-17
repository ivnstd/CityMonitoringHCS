from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models, dependencies


def is_from_administration(from_user):
    """ Является ли отправитлеь администрацией """
    stop_words = ["Администрация",
                  "Департамент",
                  "Управлябщая",
                  "Комитет",
                  "Филиал",
                  "МУПП",
                  "МКУ"]
    return any(word in from_user for word in stop_words)


async def remove_duplicate_messages(db: Session = Depends(dependencies.get_db)):
    """ Удаление дублирующих сообщений с одинаковыми датой (без времени), проблемой и адресом """
    subquery = (
        db.query(
            func.date(models.Message.date),
            models.Message.problem,
            models.Message.address
        )
        .group_by(
            func.date(models.Message.date),
            models.Message.problem,
            models.Message.address
        )
        .having(func.count() > 1)
        .subquery()
    )

    duplicates = (
        db.query(models.Message)
        .join(subquery,
              func.date(models.Message.date) == subquery.c.date)
        .filter(models.Message.problem == subquery.c.problem)
        .filter(models.Message.address == subquery.c.address)
        .all()
    )

    # Удаляем все дублирующие записи, оставляя только одну
    for i, duplicate in enumerate(duplicates):
        if i > 0:
            db.delete(duplicate)

    db.commit()
