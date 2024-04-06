# Discord Bot

This Discord bot provides various fun and interactive features for users within a Discord server.

## Features

### Currency System
- Users can earn, spend, and manage virtual currency within the server.
- Commands include:
  - `/balance`: View your current balance.
  - `/leaderboard`: View the top users by balance.
  - `/slots <bet>`: Play the slots game and win virtual currency.
  - `/blackjack <bet>`: Play a game of blackjack against the dealer.
  - `/steal <target>`: Steal money from another user.

### Mini-Games
- Enjoy various mini-games within the server, including slots, blackjack and horse racing.
- Earn rewards and compete with other users for the top spot on the leaderboard.

### Horse System
- Users can buy and upgrade virtual horses.
- Commands include:
  - `/buy-horse <horse_name>`: View available horses and purchase one.
  - `/release-horse`: Release ownership of your horse.
  - `/improve-horse-speed`: Pay to increase your horse's speed.
  - `/improve-horse-strength`: Pay to increase your horse's strength.
  - `/improve-horse-stamina`: Pay to increase your horse's stamina.
  - `/view-horse-upgrade-costs`: View the upgrade costs for your horse.
  - `/view-horse-information`: View information about your horse.

### Horse Racing
- Initiate horse races and place bets on the outcome.
- Command:
  - `/horse-race <bet_amount>`: Initiate a horse race and place a bet.

## Setup Instructions
1. Clone this repository to your local machine.
2. Install the necessary dependencies using `pip install -r requirements.txt`.
3. Set up a SQLite database to store user data, currency balances, and horse information.
4. Create a Discord bot account and obtain the token.
5. Create a `.env` file and place your token in the format `TOKEN=your_token_here`.
6. Run the bot using `BlackJack Bot.py`.

## Contributing
Contributions are welcome! If you have any suggestions, feature requests, or bug reports, please open an issue or submit a pull request.

## Credits
This bot was built using the [py-cord library](https://pycord.dev/).

## License
This project is licensed under the GPL V3 License - see the [LICENSE](https://github.com/furthestgoose/Economy-Bot/blob/main/LICENSE) file for details.
