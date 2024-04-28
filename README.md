# TDC-Econ

### TODO
 - RSS Feed to update stuff?
   - Wtf even is an RSS feed lmao
   - Maybe just use websockets like normal people
 - Investments:
   - Buy/Sell stocks (Done)
   - Dynamic prices
 - Bets:
   - Activity
   - Person bet on
   - Idk probably just a return-on-investment value
   - Dynamic returns?
 - Admin:
   - See activities (Maybe just bets)
   - Mark activity as completed by player
 - Users:
   - PIN-code for logging in
 - Dashboard:
   - Live feed of player activities
   - Graph of price history for each player

### Config
#### Activities
All available activities for players to bet on. Eg. "I bet X will chug a beer within the next 5 minutes"
 - ROI: Return on investment. How many times the original investment should a player earn if they win the bet.
 - Time: Time before the activity must be marked as completed for the player to win the bet.
#### People
A list of all the players in the game. *start_cash* defines the amount of money a player should have at the beginning of the game. *admins* contains the names of players with admin privileges

#### configStock
Change properties for stock trading functionality
 - unitPriceRatio: How much should a single stock cost, multiplied by the players money

### To run
Install flask
From root folder:

```flask --app src/main --debug run```
