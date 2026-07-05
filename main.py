#http://qrcoder.ru/code/?https%3A%2F%2Fgithub.com%2FLolz-labs%2F&10&0
import flet as ft
import asyncio
import math
async def hub(page: ft.Page):
    page.clean()
    page.bgcolor = "#1E202B"
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#5b61b3",
            secondary="#63B3ED",
            surface="#2D3748",
            error="#E53E3E",
            on_primary="#000000",
            on_surface="#FFFFFF")
    )
    choose = ft.Text("Гомп", size=50,color=ft.Colors.WHITE)
    btn = ft.Button('Учет выпитой воды за день', icon=ft.Icons.COUNTERTOPS, on_click=lambda e: page.run_task(water, page))
    btn1 = ft.Button('Проверка координации движений', icon=ft.Icons.COUNTERTOPS, on_click=lambda e: page.run_task(coord, page))
    btn2 = ft.Button('Ограничение экранного времени', icon=ft.Icons.COUNTERTOPS, on_click=lambda e: page.run_task(screentime, page))
    page.add(
        ft.Container(
            alignment=ft.Alignment.CENTER,
            expand=True,
            padding=30,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=["#1A1B26", "#10111A"],
            ),
            content=ft.Container(
                width=360,
                padding=25,
                border_radius=20,
                bgcolor="#16161E",
                border=ft.Border.all(1, "#24283B"),
                shadow=ft.BoxShadow(
                    blur_radius=25,
                    color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                    offset=ft.Offset(0, 10),
                ),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    tight=True,
                    controls=[
                        ft.Container(content=choose, margin=ft.Margin.only(bottom=10)),
                        btn,
                        btn1,
                        btn2
                    ]
                )
            )
        )
    )
    page.update()
async def water(page: ft.Page):
    page.clean()
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    counter = ft.Text('0 мл', size=50, data=0,color=ft.Colors.WHITE)
    remain = ft.Text('', size=20, data=2500,color=ft.Colors.WHITE)
    progress = ft.ProgressBar(width=400, value=0, color="#5b61b3", bgcolor="755d9a")
    storage = ft.SharedPreferences()
    if await storage.contains_key("waterdata"):
        saved_water = await storage.get("waterdata")
        counter.data = min(int(saved_water or 0), remain.data)
    else:
        counter.data = 0
    def update_ui():
        is_full = counter.data >= remain.data
        btn_half.disabled = is_full
        btn_full.disabled = is_full
        progress.value = counter.data / remain.data
        if is_full:
            counter.value = f"{remain.data} мл "
            remain.value = "Норма выполнена! Отличная работа!"
        else:
            counter.value = f"{counter.data} мл"
            remain.value = f"{remain.data - counter.data} мл вам осталось выпить чтобы закрыть суточную норму!"
    async def save(e, amount):
        if counter.data < remain.data:
            counter.data = min(counter.data + amount, remain.data)
            await storage.set("waterdata", counter.data)
            update_ui()
            page.update()
    async def reset(e):
        counter.data = 0
        await storage.set("waterdata", 0)
        update_ui()
        page.update()
    btn = ft.FloatingActionButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.run_task(hub, page))
    btn_half = ft.Button("Пол стакана воды 🥛", on_click=lambda e: page.run_task(save, e, 100))
    btn_full = ft.Button("Стакан воды 🥛", on_click=lambda e: page.run_task(save, e, 200))
    btn_reset = ft.Button("Сбросить прогресс 🔄", on_click=lambda e: page.run_task(reset, e))
    update_ui()
    page.add(
        counter, 
        progress, 
        remain, 
        ft.Container(),
        ft.Row([btn_half, btn_full], alignment=ft.MainAxisAlignment.CENTER), 
        ft.Row([btn_reset, btn], alignment=ft.MainAxisAlignment.CENTER)
    )
async def screentime(page: ft.Page):
    page.clean()
    time_limit = 60
    def set_limit(e):
        nonlocal time_limit
        time_limit = int(time_slider.value) * 60
    async def close_alert(e):
        dlg.open=False
        page.overlay.remove(dlg)
        dlg.update()  
    async def show_alert(e):
        page.overlay.append(dlg) 
        dlg.open = True         
        page.update()
    if not hasattr(page, "timer_task"):
        page.timer_task = None
    async def timerf(timer, page, status_text):
        try:
            while timer > 0:
                status_text.value = f"Осталось: {timer} сек."
                page.update()
                await asyncio.sleep(1)
                timer -= 1
            status_text.value = "Таймер завершен!"
            await show_alert(page)
        
        except asyncio.CancelledError:
            status_text.value = "Таймeр отменен."
            page.update()
            raise
    async def start_timer(seconds, page, status_text):
        if page.timer_task and not page.timer_task.done():
            return
        page.timer=seconds
        page.timer_task = asyncio.create_task(timerf(seconds, page, status_text))
    async def cancel_timer():
        if page.timer_task and not page.timer_task.done():
            page.timer_task.cancel()
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Вы превысили лимит времени на сегодня!"),
        content=ft.Text("Возьмите перерыв и сфокусируйтесь на делах!"),
        actions=[
            ft.TextButton("ОК", on_click=close_alert),
        ],
    )   
    txt=ft.Text('Выберите ограничение по времени')
    btn = ft.FloatingActionButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.run_task(hub, page))
    stopbtn = ft.FloatingActionButton(icon=ft.Icons.CLOSE,on_click=lambda e: asyncio.create_task(cancel_timer()))
    confirmbtn=ft.FloatingActionButton(icon=ft.Icons.PLAY_ARROW,on_click=lambda e:asyncio.create_task(start_timer(time_limit,page,txt)))
    time_slider = ft.Slider(
        min=1,
        max=120,
        divisions=119,
        value=1,
        label="{value} мин",
        on_change=set_limit
    )
    page.add(
        ft.Container(
            alignment=ft.Alignment.CENTER,
            expand=True,
            content=ft.Container(
                width=300,
                padding=20,
                border_radius=15,
                bgcolor="#ffffff",
                shadow=ft.BoxShadow(
                    blur_radius=15,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                    offset=ft.Offset(0, 5),
                ),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                    tight=True,
                    controls=[
                        txt,
                        time_slider,
                        ft.Row(controls=[btn,stopbtn,confirmbtn], spacing=45)
                    ]
                )
            )
        ))
    page.update()
async def coord(page: ft.Page):
    page.clean()
    time_left = 10
    is_testing = False
    vibration_history = []
    status_text = ft.Text("Нажмите кнопку для начала теста")
    timer_text = ft.Text("Осталось: 10 сек")
    live_force_text = ft.Text("Текущее ускорение: 0.00 m/s²")
    async def start_test(e):
        nonlocal is_testing, time_left, vibration_history
        is_testing = True
        time_left = 60
        vibration_history.clear()
        start_btn.disabled = True
        status_text.value = "Идет тест, держите телефон неподвижно"
        page.update()

        while time_left > 0:
            await asyncio.sleep(1)
            time_left -= 1
            timer_text.value = f"Осталось: {time_left} сек"


        is_testing = False
        start_btn.disabled = False

        # Подсчет результатов по пиковому вектору
        if vibration_history:
            max_vibration = max(vibration_history)
            if max_vibration < 0.35:
                status_text.value = f"Тест завершен: Тремор отсутствует (Пик: {max_vibration:.2f})"
            elif max_vibration < 1.4:
                status_text.value = f"Тест завершен: Легкий тремор (Пик: {max_vibration:.2f})"
            else:
                status_text.value = f"Тест завершен: Сильный тремор (Пик: {max_vibration:.2f})"
        else:
            status_text.value = "Ошибка: Данные не получены"
            
        page.update()
    
    def handle_reading(e: ft.UserAccelerometerReadingEvent):
        force = math.sqrt(e.x**2 + e.y**2 + e.z**2)
        vibration_history.append(force)
        
        live_force_text.value = f"Текущее ускорение: {force:.2f} m/s²"

    def handle_error(e: ft.SensorErrorEvent):
        page.add(ft.Text(f"UserAccelerometer error: {e.message}"))

    accelerometer = ft.UserAccelerometer(
        on_reading=handle_reading,
        on_error=handle_error,
        interval=ft.Duration(milliseconds=20)
    )
    page.services.append(accelerometer)

    start_btn = ft.ElevatedButton("Старт", on_click=start_test)
    btn = ft.FloatingActionButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.run_task(hub, page))
    page.add(
        ft.Container(
        alignment=ft.Alignment.CENTER, 
        content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                    tight=True,
                    controls=[
                        timer_text,
                        live_force_text,
                        status_text,
                        start_btn,
                        btn,

                    ]
                )
            )    
        )


ft.run(hub)
