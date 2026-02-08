from Selenium.project.booking.booking import Booking, logger

with Booking() as bot:
    bot.land_first_page()
    bot.change_currency("USD")
    bot.select_place_to_go("New York")
    bot.select_check_dates(check_in_date="2024-08-22", check_out_date="2023-09-22")
    bot.select_adults(10)
    bot.apply_filtration()
    bot.report()
    logger.info("Exiting.....")
