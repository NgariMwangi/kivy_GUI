import json
from datetime import datetime
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

class TableApp(App):
    product_id_counter = 1  # Counter for product ID
    sales_id_counter = 1  # Counter for sales ID

    def build(self):
        self.screen_manager = ScreenManager()

        # Create screens
        self.splash_screen = Screen(name='splash')
        self.main_screen = Screen(name='main')
        self.sales_screen = Screen(name='sales')

        # Build layouts for each screen
        self.splash_screen.add_widget(self.build_splash_layout())
        self.main_screen.add_widget(self.build_main_layout())
        self.sales_screen.add_widget(self.build_sales_layout())

        # Add screens to the ScreenManager
        self.screen_manager.add_widget(self.splash_screen)
        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.sales_screen)

        # Show splash screen initially
        return self.screen_manager

    def build_splash_layout(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        label = Label(text='Welcome to Duka Sales Management System', font_size='24sp', halign='center')
        layout.add_widget(label)
        
        # Schedule to switch to main screen after 3 seconds
        Clock.schedule_once(self.switch_to_main_screen, 7)

        return layout

    def switch_to_main_screen(self, *args):
        self.screen_manager.current = 'main'
    
    def build_main_layout(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Table header
        header = GridLayout(cols=6, size_hint_y=None, height=50)
        header.add_widget(Label(text='Product Name', bold=True))
        header.add_widget(Label(text='Quantity', bold=True))
        header.add_widget(Label(text='Selling Price', bold=True))
        header.add_widget(Label(text='Buying Price', bold=True))
        header.add_widget(Label(text='Sales', bold=True))
        header.add_widget(Label(text='View Sale', bold=True))
        layout.add_widget(header)
        
        # Scrollable table body
        self.table_data = GridLayout(cols=6, size_hint_y=None)
        self.table_data.bind(minimum_height=self.table_data.setter('height'))

        scroll_view = ScrollView(size_hint=(1, 1), size=(500, 400))
        scroll_view.add_widget(self.table_data)
        layout.add_widget(scroll_view)

        # Read data from file and populate the table
        self.read_data_from_file('data.txt')
        
        # Add button to add new product
        add_product_button = Button(text='Add Product', size_hint_y=None, height=50)
        add_product_button.bind(on_press=self.show_add_product_popup)
        layout.add_widget(add_product_button)

        return layout

    def go_to_main_screen(self, instance):
        self.screen_manager.current = 'main'

    def build_sales_layout(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Sales header
        header = GridLayout(cols=3, size_hint_y=None, height=50)
        header.add_widget(Label(text='Sales ID', bold=True))
        header.add_widget(Label(text='Quantity', bold=True))
        header.add_widget(Label(text='Sold At', bold=True))
        layout.add_widget(header)
        
        # Scrollable sales body
        self.sales_data = GridLayout(cols=3, size_hint_y=None)
        self.sales_data.bind(minimum_height=self.sales_data.setter('height'))

        scroll_view = ScrollView(size_hint=(1, 1), size=(500, 400))
        scroll_view.add_widget(self.sales_data)
        layout.add_widget(scroll_view)
     
        # Back button to return to the main screen
        back_button = Button(text='Back', size_hint_y=None, height=50)
        back_button.bind(on_press=self.go_to_main_screen)
        layout.add_widget(back_button)

        return layout

    def read_data_from_file(self, file_path):
        with open(file_path, 'r') as file:
            self.data = json.load(file)
            for item in self.data:
                self.add_row_with_data(item)

        # Set the next available product ID
        if self.data:
            self.product_id_counter = max(item['id'] for item in self.data) + 1

    def add_row_with_data(self, item):
        self.table_data.add_widget(TextInput(text=item['name'], size_hint_y=None, height=50))
        quantity_input = TextInput(text=str(item['st']), size_hint_y=None, height=50)
        self.table_data.add_widget(quantity_input)
        self.table_data.add_widget(TextInput(text=str(item['sp']), size_hint_y=None, height=50))
        self.table_data.add_widget(TextInput(text=str(item['bp']), size_hint_y=None, height=50))
        
        make_sale_button = Button(text='Make Sale', size_hint_y=None, height=50)
        make_sale_button.bind(on_press=lambda instance, item=item, quantity_input=quantity_input: self.show_sale_popup(item, quantity_input))
        self.table_data.add_widget(make_sale_button)

        view_sale_button = Button(text='View Sale', size_hint_y=None, height=50)
        view_sale_button.bind(on_press=lambda instance, item=item: self.show_sales_page(item))
        self.table_data.add_widget(view_sale_button)

    def show_sale_popup(self, item, quantity_input):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        sale_quantity_input = TextInput(hint_text='Enter quantity', size_hint_y=None, height=50)
        popup_layout.add_widget(sale_quantity_input)

        submit_button = Button(text='Submit', size_hint_y=None, height=50)
        submit_button.bind(on_press=lambda instance: self.make_sale(item, sale_quantity_input.text, quantity_input))
        popup_layout.add_widget(submit_button)

        popup = Popup(title='Make Sale', content=popup_layout, size_hint=(0.8, 0.4))
        popup.open()
        self.current_popup = popup

    def make_sale(self, item, quantity, quantity_input):
        try:
            quantity = int(quantity)
            current_stock = int(item['st'])
            
            if quantity > current_stock:
                print("Insufficient stock to make the sale")
                return

            item['st'] = current_stock - quantity  # Deduct the sale quantity from the stock quantity
            
            sale_record = {
                'sales_id': TableApp.sales_id_counter,
                'product_id': item['id'],
                'quantity': quantity,
                'sold_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            TableApp.sales_id_counter += 1
            self.update_sales_file(item['name'], sale_record)
            print(f"Made sale of {quantity} units of {item['name']} at {sale_record['sold_at']}")
            
            # Update the displayed stock quantity in the table
            quantity_input.text = str(item['st'])
            self.update_data_file()

        except ValueError:
            print("Invalid quantity entered")

        self.current_popup.dismiss()

    def update_sales_file(self, product_name, sale_record):
        try:
            with open('sales.txt', 'r') as file:
                sales_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            sales_data = []

        sale_record['product_name'] = product_name  # Add product name to the sale record
        sales_data.append(sale_record)

        with open('sales.txt', 'w') as file:
            json.dump(sales_data, file, indent=4)
    
    def update_data_file(self):
        with open('data.txt', 'w') as file:
            json.dump(self.data, file, indent=4)

    def show_sales_page(self, item):
        self.sales_data.clear_widgets()
        
        try:
            with open('sales.txt', 'r') as file:
                sales_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            sales_data = []

        product_sales = [sale for sale in sales_data if sale['product_id'] == item['id']]

        for sale in product_sales:
            self.sales_data.add_widget(Label(text=str(sale['sales_id']), size_hint_y=None, height=50))
            self.sales_data.add_widget(Label(text=str(sale['quantity']), size_hint_y=None, height=50))
            self.sales_data.add_widget(Label(text=sale['sold_at'], size_hint_y=None, height=50))

        self.screen_manager.current = 'sales'

    def show_add_product_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.product_name_input = TextInput(hint_text='Product Name', size_hint_y=None, height=50)
        popup_layout.add_widget(self.product_name_input)
        
        self.quantity_input = TextInput(hint_text='Quantity', size_hint_y=None, height=50)
        popup_layout.add_widget(self.quantity_input)
        
        self.selling_price_input = TextInput(hint_text='Selling Price', size_hint_y=None, height=50)
        popup_layout.add_widget(self.selling_price_input)
        
        self.buying_price_input = TextInput(hint_text='Buying Price', size_hint_y=None, height=50)
        popup_layout.add_widget(self.buying_price_input)

        add_button = Button(text='Add', size_hint_y=None, height=50)
        add_button.bind(on_press=self.add_product_to_file)
        popup_layout.add_widget(add_button)

        popup = Popup(title='Add Product', content=popup_layout, size_hint=(0.8, 0.6))
        popup.open()

    def add_product_to_file(self, instance):
        product_name = self.product_name_input.text
        quantity = self.quantity_input.text
        selling_price = self.selling_price_input.text
        buying_price = self.buying_price_input.text

        if product_name and quantity.isdigit() and selling_price.isdigit() and buying_price.isdigit():
            new_product = {
                'id': TableApp.product_id_counter,
                'name': product_name,
                'st': int(quantity),
                'sp': int(selling_price),
                'bp': int(buying_price)
            }
            TableApp.product_id_counter += 1
            self.data.append(new_product)
            self.update_data_file()
            self.add_row_with_data(new_product)
        else:
            print("Invalid input data")

        self.current_popup.dismiss()

if __name__ == '__main__':
    TableApp().run()
