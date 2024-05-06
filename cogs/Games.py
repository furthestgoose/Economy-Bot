from discord.ext import commands
import sqlite3
import discord
import random


class MyView(discord.ui.View):
    def __init__(self, ctx, game, bet, user_id):
            super().__init__()
            self.ctx = ctx
            self.game = game
            self.bet = bet
            self.user_id = user_id
            self.conn = sqlite3.connect('currency.db')
            self.c = self.conn.cursor()

    @discord.ui.button(label="Hit", row=0, style=discord.ButtonStyle.green)
    async def hit_button_callback(self, button, interaction):
        self.game.player_hit()
        if self.game.calculate_hand_value(self.game.player_hand) < 21:
            await interaction.response.edit_message(content=f"Your Hand: {self.game.display_player_hand()}\n Total: {self.game.calculate_hand_value(self.game.player_hand)}")       
        else:
            embed = discord.Embed(
                title= "Blackjack",
                description="You have gone bust, dealer wins",
                color=discord.Colour.red(),
            )
            await interaction.response.edit_message(embed=embed, view=None)
            guild_id = self.ctx.guild.id  # Retrieve guild ID
            self.c.execute('UPDATE currency SET balance = balance - ? WHERE guild_id = ? AND user_id = ?', (self.bet, guild_id, self.user_id))
            self.conn.commit()
            await interaction.followup.send(f"You lost {self.bet:,} coins")
    @discord.ui.button(label="Double Down", row=0, style=discord.ButtonStyle.primary)
    async def double(self,button, interaction):
        user_id = self.ctx.author.id
        guild_id = self.ctx.guild.id 
        self.c.execute('SELECT balance FROM currency WHERE guild_id = ? AND user_id = ?', (guild_id, user_id))
        row = self.c.fetchone()
        if row[0] < self.bet*2:
            embed = discord.Embed(
                title= "Blackjack",
                description=f"Your Hand: {self.game.display_player_hand()}\n Total: {self.game.calculate_hand_value(self.game.player_hand)}\n You don't have enough coins to double down!",
                color=discord.Colour.dark_gold(),
            )
            await interaction.response.edit_message(embed=embed) 
        else:
            self.game.player_hit()
            if self.game.calculate_hand_value(self.game.player_hand) < 21:
                self.game.dealer_turn()
                winner = self.game.determine_winner()
                player_hand_str = self.game.display_player_hand()
                dealer_hand_str = self.game.display_dealer_hand()  # New line to get dealer's hand
                embed = discord.Embed(
                    title= "Blackjack",
                    description=f"Your Hand: {player_hand_str}\nTotal: {self.game.calculate_hand_value(self.game.player_hand)}\nDealer's Hand: {dealer_hand_str}\nTotal: {self.game.calculate_hand_value(self.game.dealer_hand)}\nThe game is over! Winner: {winner}",
                    color=discord.Colour.dark_gold(),
                )
                await interaction.response.edit_message(embed=embed, view=None)
                if winner == "Player":
                    self.c.execute('UPDATE currency SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (self.bet*4, guild_id, user_id))
                    self.conn.commit()
                    await interaction.followup.send(f"You've won {self.bet*3:,} coins")
                elif winner == "Push":
                    self.c.execute('UPDATE currency SET balance = balance WHERE guild_id = ? AND user_id = ?', (self.bet, guild_id, user_id))
                    self.conn.commit()
                    await interaction.followup.send(f"It's a push, you get your bet back")
                else:
                    self.c.execute('UPDATE currency SET balance = balance - ? WHERE guild_id = ? AND user_id = ?', (self.bet*2, guild_id, user_id))
                    self.conn.commit()
                    await interaction.followup.send(f"You lost {self.bet*2:,} coins") 
            else:
                embed = discord.Embed(
                    title= "Blackjack",
                    description="You have gone bust, dealer wins",
                    color=discord.Colour.red(),
                )
                await interaction.response.edit_message(embed=embed, view=None)
                self.c.execute('UPDATE currency SET balance = balance - ? WHERE guild_id = ? AND user_id = ?', (self.bet*2, guild_id, user_id))
                self.conn.commit()
                await interaction.followup.send(f"You lost {self.bet*2:,} coins")



    @discord.ui.button(label="Stand", row=0, style=discord.ButtonStyle.red)
    async def stand_button_callback(self, button, interaction):
        self.game.dealer_turn()
        winner = self.game.determine_winner()
        player_hand_str = self.game.display_player_hand()
        dealer_hand_str = self.game.display_dealer_hand()  # New line to get dealer's hand
        embed = discord.Embed(
            title= "Blackjack",
            description=f"Your Hand: {player_hand_str}\nTotal: {self.game.calculate_hand_value(self.game.player_hand)}\nDealer's Hand: {dealer_hand_str}\nTotal: {self.game.calculate_hand_value(self.game.dealer_hand)}\nThe game is over! Winner: {winner}",
            color=discord.Colour.dark_gold(),
        )
        await interaction.response.edit_message(embed=embed, view=None)
        if winner == "Player":
            guild_id = self.ctx.guild.id  # Retrieve guild ID
            self.c.execute('UPDATE currency SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (self.bet, guild_id, self.user_id))
            self.conn.commit()
            await interaction.followup.send(f"You've won {self.bet:,} coins")
        else:
            guild_id = self.ctx.guild.id  # Retrieve guild ID
            self.c.execute('UPDATE currency SET balance = balance - ? WHERE guild_id = ? AND user_id = ?', (self.bet, guild_id, self.user_id))
            self.conn.commit()
            await interaction.followup.send(f"You lost {self.bet:,} coins")
            
class BlackjackGame:
    def __init__(self, player_id):
        self.player_id = player_id
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.deal_initial_cards()

    def create_deck(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        deck = [{'rank': rank, 'suit': suit} for rank in ranks for suit in suits]
        random.shuffle(deck)
        return deck

    def deal_initial_cards(self):
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]

    def calculate_hand_value(self, hand):
        total_value = 0
        num_aces = 0
        
        # Calculate the value of each card in the hand
        for card in hand:
            rank = card['rank']
            if rank in ['J', 'Q', 'K']:
                total_value += 10
            elif rank == 'A':
                num_aces += 1
                total_value += 11
            else:
                total_value += int(rank)
        
        # Adjust the value of Aces if necessary to avoid busting
        while total_value > 21 and num_aces > 0:
            total_value -= 10
            num_aces -= 1
        
        return total_value

    def player_hit(self):
        if self.calculate_hand_value(self.player_hand) < 21:
            self.player_hand.append(self.deck.pop())
            return True
        else:
            return False

    def dealer_turn(self):
        while self.calculate_hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())

    def determine_winner(self):
        player_value = self.calculate_hand_value(self.player_hand)
        dealer_value = self.calculate_hand_value(self.dealer_hand)

        if player_value > 21:
            return "Dealer"  # Player busts, dealer wins
        elif dealer_value > 21:
            return "Player"  # Dealer busts, player wins
        elif player_value > dealer_value:
            return "Player"  # Player has higher hand value, player wins
        elif player_value < dealer_value:
            return "Dealer"  # Dealer has higher hand value, dealer wins
        else:
            return "Push"

    def display_player_hand(self):
        hand_str = ', '.join([f"{card['rank']} of {card['suit']}" for card in self.player_hand])
        return hand_str
    def display_dealer_hand(self):  # New method to display dealer's hand
        hand_str = ', '.join([f"{card['rank']} of {card['suit']}" for card in self.dealer_hand])
        return hand_str
class Games(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.conn = sqlite3.connect('currency.db')
        self.c = self.conn.cursor()


    @discord.slash_command(name="blackjack", description="Play a game of blackjack")
    async def start_game(self, ctx, bet: int):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        self.c.execute('SELECT balance FROM currency WHERE guild_id = ? AND user_id = ?', (guild_id, user_id))
        row = self.c.fetchone()

        if row is None:
            await ctx.respond("You don't have a balance yet. Use `!register` to create an account.")
            return

        if row[0] < bet:
            await ctx.respond("You don't have enough coins for this bet.")
            return

        game = BlackjackGame(ctx.author.id)
        view = MyView(ctx, game, bet, user_id)

        # Check for natural 21
        player_value = game.calculate_hand_value(game.player_hand)
        dealer_value = game.calculate_hand_value(game.dealer_hand)

        if player_value == 21 and dealer_value != 21:
            await ctx.respond("Congratulations! You have a natural 21! You win!")
            self.c.execute('UPDATE currency SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (bet*2, guild_id, user_id))
            self.conn.commit()
            await ctx.send(f"You've won {bet*2:,} coins")
            return
        elif dealer_value == 21 and player_value != 21:
            await ctx.respond("Sorry, the dealer has a natural 21. You lose.")
            self.c.execute('UPDATE currency SET balance = balance - ? WHERE guild_id = ? AND user_id = ?', (bet, guild_id, user_id))
            self.conn.commit()
            await ctx.send(f"You lost {bet:,} coins")
            return
        elif player_value == 21 and dealer_value == 21:
            await ctx.respond("Both you and the dealer have natural 21s. It's a push.")
            return

        # If no natural 21s, continue with the game
        player_hand_str = game.display_player_hand()
        player_total = game.calculate_hand_value(game.player_hand)
        dealer_first_card = f"{game.dealer_hand[0]['rank']} of {game.dealer_hand[0]['suit']}"
        await ctx.respond(f"Your hand: {player_hand_str}\nTotal: {player_total}\nDealer's first card: {dealer_first_card}\nThe dealer stands on 17", view=view)

    @discord.slash_command(name="slots", description="Play the Slots")
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def slot(self, ctx, bet: int):
        guild_id = ctx.guild.id
        user_id = ctx.author.id

        # Check the user's balance in the guild
        self.c.execute('SELECT balance FROM currency WHERE guild_id = ? AND user_id = ?', (guild_id, user_id))
        row = self.c.fetchone()

        if row is None:
            # If the user doesn't have a balance in the guild, insert a new row with default balance
            self.c.execute('INSERT INTO currency (guild_id, user_id) VALUES (?, ?)', (guild_id, user_id))
            self.conn.commit()
            balance = 0
        else:
            balance = row[0]

        if balance < bet:
            await ctx.respond("You don't have enough coins for this bet.")
            return

        symbols = ['\U0001F34E', '\U0001F352', '\U0001F36C', '\U0001F34A', '\U0001F347', '\U0001F349', '\U0001F353']
        symbol_probabilities = [0.22, 0.18, 0.14, 0.12, 0.12, 0.1, 0.12]
        spin_result = [random.choices(symbols, weights=symbol_probabilities)[0] for _ in range(3)]
        result_str = "".join(spin_result)

        # Create an embed
        embed = discord.Embed(
            title="Slot Machine",
            description=result_str,
            color=discord.Color.random()
        )

        # Check for winning combinations
        if len(set(spin_result)) == 2:
            await ctx.respond(content=f"Congratulations! You won {bet*2:,} coins for two matches!", embed=embed)
            self.c.execute('UPDATE currency SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (bet*3, guild_id, user_id))
            self.conn.commit()
        elif len(set(spin_result)) == 1:
            await ctx.respond(content=f"Congratulations! You won {bet*5:,} coins for three matches!", embed=embed)
            self.c.execute('UPDATE currency SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (bet*10, guild_id, user_id))
            self.conn.commit()
        else:
            await ctx.respond(content=f"You lost {bet:,} coins, better luck next time!", embed=embed)
            self.c.execute('UPDATE currency SET balance = balance - ? WHERE guild_id = ? AND user_id = ?', (bet, guild_id, user_id))
            self.conn.commit()
            
    @slot.error
    async def slot_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = error.retry_after
            embed = discord.Embed(
                title="Cooldown",
                description=f"You can only initiate slots once every 2 minutes. Try again in {int(retry_after):,} seconds.",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Games(bot))