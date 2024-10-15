from playwright.sync_api import Page, TimeoutError, Response
from data.environment import host


class Base:
    def __init__(self, page: Page):
        self.page = page

    def open(self, uri) -> Response | None:
        return self.page.goto(f"{host.get_base_url()}{uri}", wait_until='domcontentloaded')

    def click(self, locator: str) -> None: #клик, при необходимости сам делает скролл к нужному элементу
        self.page.click(locator)

    def input(self, locator: str, data: str) -> None: #ввод в поле
        self.page.locator(locator).fill(data)

    def get_text(self, locator: str, index: int) -> str: #достаем текст, если локатор один, то в аргумент прокидываем значение 0
        return self.page.locator(locator).nth(index).text_content()

    def click_element_by_index(self, locator: str, index: int) -> None: #находим элемент по индексу и кликаем
        self.page.locator(locator).nth(index).click()

    def input_value_by_index(self, locator: str, index: int, data: str) -> None: #вводим данные в нужные поля по индексу
        self.page.locator(locator).nth(index).fill(data)


    def wait_for_element(self, locator, timeout=12000) -> None: #ожидание какого то элемента если нужно
        self.page.wait_for_selector(locator, timeout=timeout)

    def wait_for_all_elements(self, locator, timeout=5000):  #ожидание всех элементов
        elements = self.page.query_selector_all(locator)

        for element in elements:
            self.page.wait_for_selector(locator, timeout=timeout)

        return elements


    def current_url(self) -> str: #возвращает урл
        return self.page.url

    def checkbox_by_index(self, locator: str, index: int): #находим чекбокс по инкдексу и кликаем
        elements = self.page.query_selector_all(locator)
        # Проверка наличия элемента с указанным индексом
        if 0 <= index < len(elements):
            # Поставить чек-бокс по элементу с указанным индексом
            elements[index].check()
        else:
            print(f"Элемент с индексом {index} не найден.")


    def click_first_element(self, locator: str): #кликаем по первому элементу, если по индексу выдает out of range
        self.page.locator(locator).first.click()

    def click_by_text(self, text: str): #находим элемент(кнопку)с нужным текстом внутри и кликаем
        self.page.get_by_text(text).click()

    def input_in_shadow_root(self, shadow_locator: str, shadow_input_locator: str, data: str):
        #ищем элемент в шадоуруте
        shadow_root = self.page.evaluate_handle(f'document.querySelector("{shadow_locator}").shadowRoot')
        input_element = shadow_root.evaluate_handle(f'document.querySelector("{shadow_input_locator}")')
        input_element.as_element().fill(data)


    def checkbox(self, locator: str) -> None: #проверяем является ли элемент чек-боксом и проставляем чекбокс
        self.page.locator(locator).check()

    def is_element_present(self, locator: str) -> bool:#если элемент есть то все ок
        try:
            self.page.wait_for_selector(locator, timeout=10000)
        except TimeoutError as e:
            return False
        return True

    def is_element_NOT_presence(self, locator: str) -> bool: #если элемента нет, то все ок
        try:
            self.page.wait_for_selector(locator, timeout=5000)
        except TimeoutError as e:
            return True
        return False

    def selector(self, locator: str, value: str): #выпадающи список, выбираем значение в валуе
        self.page.select_option(locator, value)

    def drag_and_drop(self, source, target): #перетаскивать из-куда то
        self.page.drag_and_drop(source, target)

    def alert_accept(self, locator: str): #сначала идет слушатель, который говорит, что нужно сделать с алертом
        self.page.on('dialog', lambda dialog: dialog.accept()) #анонимная функция обрабатывающая событие
        self.click(locator)


    def open_new_tab_and_check_presence(self, locclick, locpresence): #ожидаем открытие нового таба и свитчаемся и делаем ассерт, что нужный элемент есть на странице
        with self.page.expect_popup() as page1_info:
            self.page.click(locclick)
        page1 = page1_info.value
        page1.bring_to_front()
        loc = page1.locator(locpresence)
        expect(loc).to_be_visible(visible=True, timeout=12000)

    def close_tab(self, number): #закрываем таб и возвращаемся на предыщущий, number-номер таба который хотим закрыть
        all_tabs = self.page.context.pages
        all_tabs[number].close()

    def switch_to_previous_tab(self, number): #number - номер вкладки на которую хотим свичнуться, сначала используем этот метод, потом закрываем вкладки
        all_tabs = self.page.context.pages # Получаем список всех вкладок в контексте браузера
        new_tab = all_tabs[number] # Получаем вкладку по указанному индексу
        self.page.bring_to_front() # Переключаемся на текущую вкладку (делаем ее активной)
        self.page.wait_for_load_state()  # Ожидаем завершения загрузки страницы в текущей вкладке
        return new_tab


    def close_all_tabs_except_first(self): #закрываем все табы, кроме первогоо
        all_tabs = self.page.context.pages
        for p in range(1, len(all_tabs)):
            all_tabs[p].close()

    def refresh(self) -> Response | None: #рефреш страницы
        return self.page.reload(wait_until='domcontentloaded')

    def alert_with_double_input(self, key1, value1, key2, value2):
        # ключ значения нужно вводить в ковычках,в ключ указывать название поля, а в значение что хотим ввести
        dialog = self.page.wait_for_event('dialog')
        inputs = {key1: value1, key2: value2}
        dialog.fill(inputs)
        dialog.accept()

    def switch_to_iframe_and_click(self, iframe_locator, locator_for_click): #переключаемся на iframe по локатору и кликаем
        frame = self.page.frame_locator(iframe_locator)
        if frame is not None:
            frame.locator(locator_for_click).click()
        else:
            print("Iframe not found with the specified locator:", iframe_locator)

    def switch_to_iframe_and_input(self, iframe_locator, locator_for_input, data: str):#переключаемся на iframe по локатору и вводим нужные данные
        frame = self.page.frame_locator(iframe_locator)
        if frame is not None:
            frame.locator(locator_for_input).fill(data)
        else:
            print("Iframe not found with the specified locator:", iframe_locator)

    def get_iframe_by_index(self, index): #переходим на iframe по индексу
        return self.page.main_frame.child_frames[index]

    def switch_to_main_frame(self): #возврат на основной фрейм
        return self.page.main_frame