import sqlite3
from collections import namedtuple
import datetime

class Order(object):
    def __init__(self, customerid: int):
        self.items: list = []
        self.item: namedtuple = namedtuple("item", ["id", "quantity"])
        self.customer_id: int = customerid

    def add_item(self, itemid: int, quantity: int):
        item = self.item(itemid, quantity)
        self.items.append(item)




class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect("data.db")
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.cursor = self.conn.cursor()

    def setup(self): #makes all of the sql tables and adds the sampled customers and items
        self.create_customer_table()
        self.create_inventory_table()
        self.create_order_table()
        self.create_order_line_table()
        self.add_sampled_customers()
        self.add_sampled_items()

    """
    run sql func
    """

    def run(self, query, *args):
        self.cursor.execute(query, *args)
        self.conn.commit()
        return self.cursor.fetchall()

    """
    table creation
    """
    def create_customer_table(self):
        query = """
            CREATE TABLE CUSTOMER 
            (
            customerID INTEGER,
            customerName CHARACTER,
            address CHARACTER,
            postcode CHARACTER,
            emailAddress CHARACTER,
            primary key (customerID)
            )
        """
        return self.run(query)

    def create_inventory_table(self):
        query = """
            CREATE TABLE INVENTORY 
            (
            itemID INTEGER,
            itemName CHARACTER,
            unitPrice INTEGER, 
            quantityInStock INTEGER,
            primary key (itemID)
            )
        """
        return self.run(query)

    def create_order_table(self):
        query = """
            CREATE TABLE ORDER_ 
            (
            orderNo INTEGER,
            customerID INTEGER, 
            date_ DATE, 
            totalCost INTEGER,
            primary key (orderNo)

            CONSTRAINT fk_customer
                FOREIGN KEY (customerID)
                REFERENCES CUSTOMER(customerID)
            )
        """
        self.run(query)

    def create_order_line_table(self):
        query = """
            CREATE TABLE ORDER_LINE
            (
            orderNo INTEGER,
            itemID INTEGER,
            quantity INTEGER,
            primary key (orderNo, itemID)
            
            CONSTRAINT fk_order
                FOREIGN KEY (orderNo)
                REFERENCES ORDER_(orderNo)
            
            CONSTRAINT fk_item
                FOREIGN KEY (itemID)
                REFERENCES INVENTORY(itemID)
            )
        """
        self.run(query)

    """
    customer table related functions
    """
    def get_customer_from_email(self, email: str) -> bool | tuple:
        query = "SELECT * FROM CUSTOMER WHERE emailAddress = ?", [email]
        row = self.run(*query)
        if not row:
            return False
        else:
            return row[0]

    def get_customerid(self):
        query = """
            SELECT customerID FROM CUSTOMER ORDER BY customerID desc LIMIT 1
        """
        row = self.run(query)
        if not row:
            return 1
        else:
            return row[0][0]+1

    def add_customer(self, customername: str, address: str, postcode: str, emailaddress: str):
        customerid = self.get_customerid()
        query = "INSERT INTO CUSTOMER VALUES (?, ?, ?, ?, ?)", (
            customerid,
            customername,
            address,
            postcode,
            emailaddress
        )
        self.run(*query)

    def add_sampled_customers(self):
        customers = [
            ['Bob', '7 Master Builder Street', 'MB7 9Z1', 'Bob7@MasterBuilder.com'],
            ['Kratos', '9 Midgard Street', 'NM9 1P2', 'Kratos@godkiller.com'],
            ['Monkey', '64 zoo lane', 'L64 6R2', 'Monkey64@zoomail.com'],
            ['Saul', '14 GoodMan Street', 'IAG M14', 'itsAllGoodMan@lawyermail.com'],
            ['Franklin', '4 Grove Street', 'G84 PL3', 'Franklin@ClintonIndustries.com']
        ]
        for customer in customers:
            self.add_customer(*customer)

    """
    inventory table related functions
    """

    def get_itemid(self):
        query = """
            SELECT itemID FROM INVENTORY ORDER BY itemID desc LIMIT 1
        """
        row = self.run(query)
        if not row:
            return 1
        else:
            return row[0][0]+1

    def get_items(self):
        items = [
            [1, "PS5", 450],
            [2, "Iphone 14 Pro Max", 1400],
            [3, "Desk", 140],
            [4, "Monitor", 1800],
            [5, "Controller", 70]
        ]
        return items


    def add_item(self, itemname: str, unitprice: int, quantityinstock: int):
        itemid = self.get_itemid()
        query = "INSERT INTO INVENTORY VALUES (?, ?, ?, ?)", [itemid, itemname, unitprice, quantityinstock]
        self.run(*query)

    def add_sampled_items(self):
        items = [
            ["PS5", 450, 100],
            ["Iphone 14 Pro Max", 1400, 100],
            ["Desk", 140, 100],
            ["Monitor", 1800, 100],
            ["Controller", 70, 100]
        ]
        for item in items:
            self.add_item(*item)

    def get_stock(self, itemid: int) -> int:
        query = "SELECT quantityInStock FROM INVENTORY WHERE itemID = ?", [itemid]
        row = self.run(*query)
        if not row:
            return 0
        else:
            return row[0][0]

    def can_buy_stock(self, itemid: int, quantity: int) -> bool:
        stock = self.get_stock(itemid)
        if stock >= quantity:
            return True
        else:
            return False

    def update_stock(self, itemid: int, updatedquantity: int) -> bool:
        query = "UPDATE INVENTORY SET quantityInStock = ? WHERE itemID = ?", [updatedquantity, itemid]
        self.run(*query)

    """
    order table related functions
    """

    def get_orderno(self):
        query = """
            SELECT orderNo FROM ORDER_ ORDER BY orderNo desc LIMIT 1
        """
        row = self.run(query)
        if not row:
            return 1
        else:
            return row[0][0]+1

    def get_order_cost(self, *args) -> int:
        total_cost = 0
        for item in args:
            query = "SELECT unitPrice FROM INVENTORY WHERE itemID = ?", [item.id]
            cost = self.run(*query)
            cost = cost[0][0]
            if cost:
                cost = cost * item.quantity
                total_cost += cost
        return total_cost

    def add_order(self, customerid: int, totalcost: int) -> int:
        orderno = self.get_orderno()
        query = "INSERT INTO ORDER_ VALUES (?, ?, date('now'), ?)", [orderno, customerid, totalcost]
        self.run(*query)
        return orderno

    def add_to_order_line(self, orderno: int, itemid: int, quantity: int):
        current = self.get_stock(itemid)
        new = current - quantity
        self.update_stock(itemid, new)
        query = "INSERT INTO ORDER_LINE VALUES (?, ?, ?)", [orderno, itemid, quantity]
        self.run(*query)

    def place_order(self, orderobj: Order) -> list:
        items = orderobj.items
        total_cost = self.get_order_cost(*items)
        orderno = self.add_order(orderobj.customer_id, total_cost)
        FLAG = True
        for item in items:
            itemid, quantity = item.id, item.quantity
            res = self.can_buy_stock(itemid, quantity)
            if res == False:
                FLAG = False
                break
        if FLAG:
            for item in items:
                itemid, quantity = item.id, item.quantity
                self.add_to_order_line(orderno, itemid, quantity)
            return [orderno, total_cost]
        else:
            return []

    def get_all_orders(self, customerid: int) -> tuple:
        query = "SELECT * FROM ORDER_ WHERE customerid = ? ORDER BY date_ desc", [customerid]
        return self.run(*query)

    def cancel_order(self, orderno: int):
        query = "SELECT * FROM ORDER_LINE WHERE orderNo = ?", [orderno]
        order_line_rows = self.run(*query)
        for row in order_line_rows:
            current = self.get_stock(row[1])
            new = current + row[2]
            self.update_stock(row[1], new)
        query = "DELETE FROM ORDER_LINE WHERE orderNo = ?", [orderno]
        self.run(*query)
        query = "DELETE FROM ORDER_ WHERE orderNo = ?", [orderno]
        self.run(*query)

    """
    reports
    """

    def generate_customer_report(self, customerid: int) -> list:
        feedback = []
        query = "SELECT * FROM CUSTOMER WHERE customerID = ?", [customerid]
        customer_info = self.run(*query)[0]
        feedback.append(f"Name:{customer_info[1]} \tID: {customerid}")
        feedback.append("\n")
        feedback.append(f"ITEMS ORDERED: \nName\t\tQuantity")
        query = "SELECT * FROM ORDER_ WHERE customerID = ?", [customerid]
        orders = self.run(*query)
        if not orders:
            return ["Customer has no orders!"]
        total_orders = len(orders)
        items = {}
        for order in orders:
            query = "SELECT itemID, quantity FROM ORDER_LINE WHERE orderNo = ?", [order[0]]
            res = self.run(*query)
            for element in res:
                if items.get(element[0], False):
                    items[element[0]] += element[1]
                else:
                    items[element[0]] = {}
                    items[element[0]] = element[1]

        for key, val in items.items():
            query = "SELECT itemName FROM INVENTORY WHERE itemID = ?", [key]
            item_name = self.run(*query)[0][0]
            feedback.append(f"{item_name}:\t\t{val}")

        feedback.append("\n")
        feedback.append(f"TOTAL ORDERS: {total_orders}")
        query = "SELECT MAX(totalCost), SUM(totalCost)  FROM ORDER_ WHERE customerID = ?", [customerid]
        res = self.run(*query)[0]
        feedback.append(f"\nLargest Order Cost: £{res[0]}")
        feedback.append(f"Sum of all Orders: £{res[1]}")
        query = "SELECT SUM(ORDER_LINE.quantity) FROM ORDER_LINE, ORDER_ WHERE ORDER_.customerID = ? and ORDER_.orderNo = ORDER_LINE.orderNo", [customerid]
        total_quantity = self.run(*query)[0][0]
        average_quantity = round(total_quantity / total_orders)
        feedback.append(f"Average quantity of items per order: {average_quantity}")
        return feedback

    def special_report(self) -> list:
        query = "SELECT customerID FROM ORDER_ WHERE date_ < date(?) and date_ > date(?)", [datetime.datetime(2023, 1, 1, 0, 0), datetime.datetime(2022, 12, 1, 0, 0)]
        res = self.run(*query)
        res = set(res)
        feedback = []
        for user in res:
            query = "SELECT CUSTOMER.customerName, CUSTOMER.emailAddress, sum(ORDER_LINE.quantity) FROM CUSTOMER, ORDER_, ORDER_LINE WHERE CUSTOMER.customerID = ? and CUSTOMER.customerID = ORDER_.customerID and ORDER_.orderNo = ORDER_LINE.orderNo", [user[0]]
            info = self.run(*query)[0]
            if info[2] > 10:
                feedback.append(f"Customer Name: {info[0]}\tEmail Address: {info[1]}\tItems Ordered: {info[2]}\n")
        return feedback


