from db import Order, Database
from fuzzywuzzy import process

class Interface(object):
    def __init__(self):
        self.db = Database()
        self.first_menu()

    def first_menu(self):
        while True:
            try:
                try:
                    getattr(self, "usertype")
                    if self.usertype == "customer":
                        user_input = input("\n____________________\n1. Place Order Menu\n2. View Orders\n3. Cancel Order\n4. Exit\n\n___________________\nEnter your choice 1-4: ")
                        user_input = int(user_input)
                        if user_input == 1:
                            self.place_order_menu()
                        elif user_input == 2:
                            self.list_orders()
                        elif user_input == 3:
                            self.cancel_order()
                        elif user_input == 4:
                            delattr(self, "usertype")
                            print("You have been Logged out...")
                        else:
                            print("please enter a valid option\nTo quit type quit, exit or stop!")
                    if self.usertype == "manager":
                        user_input = input(
                            "\n____________________\n1. Generate Customer Report\n2. Special Offer Report\n3. Exit\n\n___________________\nEnter your choice 1-3: ")
                        user_input = int(user_input)
                        if user_input == 1:
                            self.generate_customer_report()
                        elif user_input == 2:
                            self.generate_special_report()
                        elif user_input == 3:
                            delattr(self, "usertype")
                            print("You have been Logged out...")
                        else:
                            print("Please enter a valid option\nTo quit type quit, exit or stop!")

                except AttributeError: #getattr raises AttributeError when the Attribute doesnt exist
                    user_input = input(
                        "\n____________________\n1. Log in\n2. Manager Menu\n___________________\nEnter your choice 1-2: ")
                    user_input = int(user_input)
                    if user_input == 1:
                        self.login()
                    elif user_input == 2:
                        self.manager_menu()
                    else:
                        print("Please enter a valid option\nTo quit type quit, exit or stop!")
            except ValueError: #value error means the program doesnt stop if they input a non integer type
                if user_input.lower() in ["quit", "exit", "stop"]:
                    exit()

    def login(self):
        while True:
            email = input("Enter Your Email: ")
            if email.lower() in ["quit", "exit", "stop"]:
                self.first_menu()
            res = self.db.get_customer_from_email(email)
            if res != False:
                self.usertype = "customer"
                self.customerid = res[0]
                self.customername = res[1]
                break
            else:
                print("Invalid Try again\n")

        self.first_menu()

    def manager_menu(self):
        username = input("Enter username: ")
        password = input("Enter Password: ")
        if username == "Admin" and password == "Admin":
            self.usertype = "manager"
            self.first_menu()
        else:
            print("invalid username or password!")
            self.first_menu()

    def generate_customer_report(self):
        try:
            id = int(input("Enter customerid: "))
        except ValueError:
            print("Invalid ID")
            self.first_menu()
        if id < 1 and id > 5:
            print("Invalid ID")
            self.first_menu()
        feedback = self.db.generate_customer_report(id)
        for ln in feedback:
            print(ln)

    def generate_special_report(self):
        feedback = self.db.special_report()
        if feedback:
            print("Special Offer qualifiers: ")
            for ln in feedback:
                print(ln)
        else:
            print("No one qualifies for this offer!")


    def place_order_menu(self):
        try:
            getattr(self, "order")
        except AttributeError:
            self.order = Order(self.customerid)
        while True:
            try:
                user_input = input("\n____________________\n1. add item\n2. view order\n3. Clear Order\n4. place order\n\n___________________\nEnter your choice 1-4: ")
                user_input = int(user_input)
                if user_input == 1:
                    self.add_item()
                elif user_input == 2:
                    self.view_order()
                elif user_input == 3:
                    self.clear_order()
                elif user_input == 4:
                    self.place_order()
                else:
                    print("Please enter a valid option\nTo quit type quit, exit or stop!")

            except ValueError:
                if user_input.lower() in ["quit", "exit", "stop"]:
                    self.first_menu()

    def add_item(self):
        items = self.db.get_items()
        items_names = [f"{l[1]}: £{l[2]}" for l in items]
        joined_item_names = "\n".join(items_names)
        user_item = input(f"Inventory:\n{joined_item_names}\nPlease choose a item to buy: ")
        id = None
        results = process.extract(user_item, items, limit=1)
        if results[0][1] >= 75:
            id = results[0][0][0]
            actual_item = results[0][0][1]

        if id is not None:
            while True:
                quantity = input(f"Enter the Quantity of {actual_item}\'s You would like to purchase: ")
                try:
                    quantity = int(quantity)
                    break
                except ValueError:
                    if quantity in ["exit", "quit", "stop"]:
                        self.first_menu()
                    print("Not a valid Number!")

            self.order.add_item(id, quantity)
            print(f"Added to Order\n\titem name: {actual_item}\tQuantity: {quantity}")
            self.place_order_menu()

        else:
            print("Invalid Item!")

    def view_order(self):
        items = self.order.items
        if items == []:
            print("No items in your order!")
            return
        items_dict = {1: "PS5", 2: "Iphone 14 Pro Max", 3: "Desk", 4: "Monitor", 5: "Controller"}
        print("YOUR CURRENT ORDER")
        for item in items:
            name = items_dict[item.id]
            print(f"Name: {name}, Quantity: {item.quantity}")

    def clear_order(self):
        delattr(self, "order")
        print("deleted your current order\nRedirecting you to the main menu!")
        self.first_menu()

    def place_order(self):
        if self.order.items == []:
            print("No items in your order!")
            return
        res = self.db.place_order(self.order)
        if res == []:
            print("There is not enough stock to meet your order demand\nYour order has been cancelled!")
        else:
            print(f"Order Placed\nYour order number is {res[0]}\nTotal Cost: {res[1]}")
            delattr(self, "order")
            self.first_menu()

    def list_orders(self, *, return_val=False) -> bool | None:
        res = self.db.get_all_orders(self.customerid)
        if res:
            print("Here is a list of your orders:")
            for order in res:
                print(f"Order Number: {order[0]}\tTotal Cost: {order[3]}\tDate: {order[2]}")
            if return_val:
                return True
        else:
            print("You have no orders...")
            if return_val:
                return False

        self.first_menu()

    def cancel_order(self):
        res = self.list_orders(return_val=True)
        if res:
            while True:
                orderno = input("Provide the order number for the order you would like to cancel: ")
                try:
                    orderno = int(orderno)
                    break
                except ValueError:
                    if orderno.lower() in ["exit", "quit", "stop"]:
                        self.first_menu()
            self.db.cancel_order(orderno)
            print("order has been cancelled!")

        self.first_menu()


if __name__ == "__main__":
    Interface()