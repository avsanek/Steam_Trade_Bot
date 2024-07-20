# variables for working with auto_buy
"""
    settings for search range of items on the web-parse steam item
'ot_buy' - from how many dollars, 'ot_prof' - from percentage profit, 'do_prof' - before percentage profit,
'weak' - from how many sales a week
"""
tradeback_set: dict[str, str] = {'ot_buy': '0.5', 'ot_prof': '-3', 'do_prof': '', 'weak': '250'}

"""
    settings for purchasing an item
'ot_buy' - how much is the maximum sales percentage per hour, 'dota_prof' - profit percentage Dota,
'cs_go_prof' - profit percentage CS_GO
"""
game_set: dict[str, float] = {'buy_in_Hour': 20.0, 'dota_prof': 1.7, 'cs_go_prof': 2.5}

"""
    settings for search range of items (for all possible ranges)
    1) from how many dollars 2) up to how many dollars 3) from percentage profit 4) profit percentage Dota
    5) profit percentage CS_GO 6) status of calculate
"""
spisoc_range_prof: list[list[str | float]] = [['0.4', '0.5', '0', 0.6, 0.9, 'numbers'],
                                              ['0.3', '0.4', '0', 0.5, 0.75, 'numbers'],
                                              ['0.1', '0.3', '0', 0.4, 0.6, 'numbers'],
                                              ['0', '0.1', '4', 0.4, 0.6, 'numbers'],
                                              ['0.5', '1000', '-3', 1.7, 2.5, 'procent']]

# remember main windows to use
windows: dict[str, str] = {}
