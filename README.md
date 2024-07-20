# Steam Trade Bot

Steam Trade Bot for work with https://steamcommunity.com/market/ - include placing order(buy item), refresh order and placement of the purchased item

Auto_buy it's placing a purchase order for the item. Realized on Selenium. Logging into steam - goes to the steam parser - takes the received items - if the item passes the algorithms (analyzing the item for profitability), we place an order

Auto_sell it's placement of the purchased item at the marcet.  Realized entirely through internal HTTP requests to the SteamMarket platform API and using BeautifulSoup. Checks history on items bought or sold - if the item is sold(deletes it from the database), if it is bought(gets the id of the item in the inventory) - get item_nameid of the item to connect to the item price api - calculate the selling price of the item based on the current items on the marketplace and put the item up for sale - add to the database
