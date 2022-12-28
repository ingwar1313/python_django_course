from typing import List
import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import pandas as pd


# SQLAlchemy specific code, as with any other app
DATABASE_URL = "sqlite:///./sales__.db"
print(DATABASE_URL)
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()


# Таблица продаж
sales = sqlalchemy.Table(
    "sales",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True , autoincrement=True, comment="Идентификатор покупки"),
    sqlalchemy.Column("sale_time",sqlalchemy.DateTime, comment="Дата-время покупки"),
    sqlalchemy.Column("item_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("items.id"), comment="Идентификатор товара"),
    sqlalchemy.Column("store_id",sqlalchemy.Integer, sqlalchemy.ForeignKey("stores.id"), comment="Идентификатор магазина")
)

# Таблица товаров
items = sqlalchemy.Table(
    "items",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True , autoincrement=True, comment="Идентификатор товара"),
    sqlalchemy.Column("name", sqlalchemy.String, unique=True, comment="Название товара"),
    sqlalchemy.Column("price", sqlalchemy.Float, comment="Цена товара")
)

# Таблица магазинов
stores = sqlalchemy.Table(
    "stores",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True , autoincrement=True, comment="Идентификатор магазина"),
    sqlalchemy.Column("address", sqlalchemy.String, unique=True, comment="Адрес магазина")
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
    # Уберите параметр check_same_thread когда база не sqlite
)
metadata.create_all(engine)


class Item(BaseModel):
    id: int
    name: str
    price: float

class ItemIn(BaseModel):
    name: str
    price: float

class Store(BaseModel):
    id: int
    address: str

class StoreIn(BaseModel):
    address: str

class Sales(BaseModel):
    id: int
    sale_time: datetime
    item_id: int
    store_id: int 

class SalesIn(BaseModel):
    item_id: int
    store_id: int
    sale_time = datetime.now()

class Top10Stores(BaseModel):
    store_id: int
    address: str
    income: float

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()
    # Не работает, хоть убей. хотел сделать автозаполнение, выдает ошибку. Причем саму запись добавляет
    # query_item = """INSERT INTO items (name, price) VALUES ('Чипсы', '2.3');"""
    # print(query_item)
    # await database.fetch_all(query_item)



@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/items/", response_model=List[Item])
async def read_item():
    query = items.select()
    return await database.fetch_all(query)

@app.get("/stores/", response_model=List[Store])
async def read_store():
    query = stores.select()
    return await database.fetch_all(query)

@app.get("/sales/")#, response_model=List[Sales])
async def read_sales():
    query = sales.select()
    return await database.fetch_all(query)

@app.post("/items/", response_model=Item)
async def create_item(item: ItemIn):
    query = items.insert().values(name=item.name, price = item.price)
    last_record_id = await database.execute(query)
    return {**item.dict(), "id": last_record_id}

@app.post("/stores/", response_model=Store)
async def create_store(store: StoreIn):
    query = stores.insert().values(address=store.address)
    last_record_id = await database.execute(query)
    return {**store.dict(), "id": last_record_id}

@app.post("/sales/", response_model=Sales)
async def create_sale(sale: SalesIn):
    query = sales.insert().values(item_id=sale.item_id, store_id=sale.store_id, sale_time=sale.sale_time)
    last_record_id = await database.execute(query)
    return {**sale.dict(), "id": last_record_id}

#обрабатывает GET-запрос на получение данных по топ 10 самых продаваемых товаров (id + наименование + количество проданных товаров)
@app.get("/top10items/") # , response_model=List[Sales])
async def read_top10items():
    query = r"""select id, name as 'Наименование', sales_num as 'Количество проданных товаров' from
                (select item_id, count(item_id) as sales_num
                from sales
                group by item_id
                order by sales_num desc
                limit 10) as top10sales
                left join
                items
                on 
                top10sales.item_id = items.id
                """
    return await database.fetch_all(query)

# обрабатывает GET-запрос на получение данных по топ 10 самых доходных магазинов за месяц (id + адрес + суммарная выручка)
# месяц - прошедший
# а как сделать проверку модели с русскими буквами?
@app.get("/top10stores/") #, response_model=List[Top10Stores])
async def read_top10stores():
    query = r"""select store_id as id, address as 'Адрес', income as 'Суммарная выручка' from 
                    (with sales_and_prices(sale_time, store_id, price) as 
                        (select 
                        sale_time, store_id, price
                        from sales
                        left join
                        items
                        on sales.item_id = items.id
                        where sale_time >= datetime('now', '-1 months')
                        )
                    select 
                    store_id, sum(price) as income
                    from sales_and_prices
                    group by store_id
                    order by income desc
                    limit 10
                    ) as sales_and_stores
                    left join 
                    stores
                    on sales_and_stores.store_id = stores.id"""
    # query = "SELECT datetime('now', 'start of month', '+1 months')"
    return await database.fetch_all(query)



@app.post("/stores-fillfromfile/")
async def fill_store():
    df = pd.read_excel(r"tables_fill.xlsx", sheet_name="stores")
    values = list(df["address"])
    for value in values: 
        query = stores.insert().values(address=str(value))
        last_record_id = await database.execute(query)
    return "Stores filled from file"

@app.post("/items-fillfromfile/")
async def fill_item():
    df = pd.read_excel(r"tables_fill.xlsx", sheet_name="items")
    values = list(df.values)
    for value in values: 
        query = items.insert().values(name=str(value[1]), price = float(value[2]))
        last_record_id = await database.execute(query)
    return "Items filled from file"

@app.post("/sales-fillfromfile/")
async def fill_sales():
    df = pd.read_excel(r"tables_fill.xlsx", sheet_name="sales")
    values = list(df.values)
    for value in values: 
        query = sales.insert().values(item_id=int(value[1]), store_id=int(value[2]), sale_time=datetime.now())
        last_record_id = await database.execute(query)
    return "Sales filled from file"