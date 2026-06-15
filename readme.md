# CrystalGrowthTool

Эта программа разработана для снятия данных роста с серии изображений кристаллов, снятых с помощью атомно-силового микроскопа, и сохранить результаты измерений в Excel файл.

## Возможности

- Загрузка и обработка изображений кристаллов
- Создание и редактирование линий роста
- Различные типы сеток (радиальная, вертикальная, горизонтальная, эллипсоидная) или кастомная (заданная вручную)
- Автоматическое определение пересечений линий роста с линиями сетки
- Экспорт данных после обработки в Excel
- Сохранение, открытие и закрытие файла проекта в формате .crystal
- Настраиваемые горячие клавиши

## Системные требования

- Windows
- Python 3.8 (если запуск через среду python, протестировано на этой версии)

## Установка и запуск
Скачать скомпилированный из releases по [ссылке](https://github.com/justwolk/CrystalGrowthTool/releases/latest)
Или запустить самостоятельно
```bash
git clone https://github.com/justwolk/CrystalGrowthTool.git
cd CrystalGrowthTool
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
## Компиляция в .exe
```bash
pip install pyinstaller
pyinstaller build.spec

```
## Компиляция в .ui в .py
Сгенерированные формы находятся в ui/generated. Исходники Qt Designer лежат в resources/qt_designer_files; после изменения .ui файлы нужно заново собрать в Python формат.
```bash
pyside2-uic ui_main_window.ui -o ui_main_window.py
pyside2-uic ui_start_window.ui -o ui_start_window.py
```




