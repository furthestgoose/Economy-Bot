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
  - `/steal <target>`: Steal money from another user

### Mini-Games
- Enjoy various mini-games within the server, including slots and blackjack.
- Earn rewards and compete with other users for the top spot on the leaderboard.

## Setup Instructions
1. Clone this repository to your local machine.
2. Install the necessary dependencies using `pip install -r requirements.txt`.
3. Set up a SQLite database to store user data and currency balances.
4. Create a Discord bot account and obtain the token.
5. Create a .env file.
6. Place token in format `TOKEN= your token here`.
7. Run the bot using `BlackJack Bot.py`.

## Contributing
Contributions are welcome! If you have any suggestions, feature requests, or bug reports, please open an issue or submit a pull request.

## Credits
This bot was built using the [py-cord library](https://pycord.dev/)

## License
This project is licensed under the GPL V3 License - see the [LICENSE](https://github.com/furthestgoose/Economy-Bot/blob/main/LICENSE) file for details.
