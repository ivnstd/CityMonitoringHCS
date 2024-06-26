var map;
var DATA;

let area = [[51.36797765022104,45.439861987792945], [51.71308855448513,46.57488701220701]];
let center = [51.533562, 46.034266];
let zoom = 13;


function run_map(messages) {
    DATA = messages;
    ymaps.ready(init);
}

// Функция инициализации карты
function init() {
	// Создание экземпляра карты и его привязка к контейнеру с заданным id
	map = new ymaps.Map('map', {
		center: center,
		zoom: zoom
	}, {
		// Зададим ограниченную область прямоугольником, примерно описывающим город
		restrictMapArea: area
	}),
	clusterer = new ymaps.Clusterer({
		// Макет метки кластера pieChart
		clusterIconLayout: 'default#pieChart',
		// Радиус диаграммы в пикселях
		clusterIconPieChartRadius: 20,
		// Радиус центральной части макета
		clusterIconPieChartCoreRadius: 10,
		// Ширина линий-разделителей секторов и внешней обводки диаграммы
		clusterIconPieChartStrokeWidth: 2,
		// Определяет наличие поля balloon
		hasBalloon: true
	});

	if (DATA) {
		showMarkers();
	}
	map.geoObjects.add(clusterer);         // вывод кластеров с геообъектами
	map.controls.remove('trafficControl'); // удаляем контроль трафика
}

// Функция отображения меток на карте
function showMarkers(data = DATA) {
    // Очищаем кластеризатор от предыдущих меток
    clusterer.removeAll();

    // Проходим по всем данным и добавляем метки в кластеризатор
	data.forEach(message => {
		// Используем данные каждого сообщения для отображения проблемы на карте

		// Определение цвета метки по соответствующему тегу проблемы
		let color = getColorByProblem(message.problem);

		// Преобразование координат в формат [широта, долгота]
		const [latitude, longitude] = message.coordinates.split(' ').map(parseFloat);

		let image = ''
		if (message.image) {
			image = '<div style="width: 200px; height: 108px; background-image: url(' +
			message.image + '); background-size: cover;"></div>';
		}

		// Создание и добавление метки в кластер
		clusterer.add(new ymaps.Placemark([longitude, latitude], {
			balloonContentHeader: '<b>' + message.problem + '</b>',
			balloonContentBody: image + '<br/> ' + message.address,
			balloonContentFooter: '<a href="' + message.url + '" target="_blank">' +
			message.date + '</br>' + 'Перейти к жалобе </a>',
		}, {
			preset: 'islands#dotIcon',
			iconColor: color
		}));
	});
}

// Функция для определения цвета иконки метки по типу проблемы
function getColorByProblem(problem) {
	switch (problem) {
		case 'Водоснабжение':
			return '#4FAEEE';
		case 'Теплоснабжение':
			return '#EE4B68';
		case 'Электроснабжение':
			return '#EEA849';
		case 'Дорожное хозяйство':
			return '#4CEB66';
		case 'Вывоз ТБО':
			return '#6A5ACD';
		default:
			return '#808080';
	}
}

function filterMarkers(problem) {
	// Отображаем только метки с выбранным типом проблемы
    let filteredData = DATA.filter(item => item.problem === problem);

    // Отображаем отфильтрованные метки на карте
    showMarkers(filteredData);
}