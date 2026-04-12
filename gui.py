import tkinter as tk
import random
from PIL import Image, ImageTk
from test_deal_cards.test_decks import test_decks

class BlackJackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BlackJack Game")
        height:int = 800
        width:int = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{height}x{width}+{x}+{y}")
        self.root.resizable(width=False, height=False)
        self.root.configure(bg="#076324") # casino green background
        self.font:str = "Courier New"
        self.btn_font_size:int = 12
        self.card_font_size:int = 11
        self.background_color = "#076324"
        self.card_width:int = 70
        self.card_height:int = 100

        self.card_images:dict = {}  # Cache for card images to prevent garbage collection
        self.deck:list = []  # Will hold the current deck of cards
        self.player_hand:list = []  # List to hold player's cards
        self.dealer_hand:list = []  # List to hold dealer's cards

        self.balance:int = 10000  # Starting balance for betting
        self.player_bet:int = 0  # Current bet amount
        self.player_winnings:int = 0  # Amount won from round

        self.make_deck()  # Initialize the deck of cards
        self._build_layout()
    # ------------------------------------------------------------------
    #  Deck                                                   
    # ------------------------------------------------------------------ 
    def make_deck(self):
        self.deck = []
        self.deck = test_decks().deck_82
        suits = ["hearts", "diamonds", "clubs", "spades"]
        rank = range(2, 15) # 11=Jack, 12=Queen, 13=King, 14=Ace
        for _ in range(6):  # Increase to 6 for a shoe of 6 decks
            for suit in suits:
                for r in rank:
                    #self.deck.append(f"{r}_of_{suit}")
                    pass

    def draw_from_deck(self):
        if len(self.deck) == 0:
            self.make_deck()  # Reshuffle if deck is empty
        card = random.choice(self.deck)
        self.deck.remove(card)
        return card
    
    def calculate_hand_value(self, hand):
        value = 0
        aces = 0
        for card in hand:
            rank = int(card.split("_")[0])
            if rank >= 11 and rank <= 13:  # Face cards
                value += 10
            elif rank == 14:  # Ace
                aces += 1
            else:
                value += rank
        if aces > 1:
            temp_value = value + 11 + (aces - 1)  # Count one Ace as 11 and the rest as 1
            if temp_value > 21:
                value += aces  # Count all Aces as 1
            else:
                value += 11 + (aces - 1)  # Count one Ace as 11 and the rest as 1
        elif aces == 1:
            if value + 11 > 21:
                value += 1  # Count Ace as 1
            else:
                value += 11  # Count Ace as 11
        return value
    
    def check_for_bust(self, hand):
        if self.calculate_hand_value(hand) > 21:
            self.render_hand(self.dealer_canvas, self.dealer_hand, hide_second=False)
            self.player_score_label.config(text=f"Your Score: {self.calculate_hand_value(self.player_hand)}")
            self.deal_score_label.config(text=f"Dealer's Score: {self.calculate_hand_value(self.dealer_hand)}")
            self._set_button_states(hit=tk.DISABLED, stand=tk.DISABLED, bet=tk.NORMAL)
            return True
        return False
    
    def check_blackjack(self, hand):
        if self.calculate_hand_value(hand) == 21 and len(hand) == 2:
            return True
        return False
    
    def who_won(self):
        player_score = self.calculate_hand_value(self.player_hand)
        dealer_score = self.calculate_hand_value(self.dealer_hand)

        if player_score > dealer_score:
            self.round_result_label.config(text="Round Result:\nYou win!")
            self.balance += self.player_bet  # Add winnings to balance
        elif dealer_score == player_score:
            self.round_result_label.config(text="Round Result:\nIt's a Tie!")
            self.player_bet = 0  # Reset bet for next round
        else:
            self.round_result_label.config(text="Round Result:\nDealer wins!")
            self.balance -= self.player_bet  # Deduct losses from balance
        self.balance_label.config(text=f"Balance: ${self.balance}")

    def check_hand_status(self):
        player_blackjack = self.check_blackjack(self.player_hand)
        dealer_blackjack = self.check_blackjack(self.dealer_hand)

        print(f"Player hand: {self.player_hand}")
        print(f"Dealer hand: {self.dealer_hand}")
        print(f"Player value: {self.calculate_hand_value(self.player_hand)}")
        print(f"Dealer value: {self.calculate_hand_value(self.dealer_hand)}")
        print(f"Player BJ: {player_blackjack}, Dealer BJ: {dealer_blackjack}")

        if dealer_blackjack and player_blackjack:
            print("Branch: both blackjack")
            self.player_bet = 0
            self._end_round("Stand-off. Bets returned!")
        elif dealer_blackjack:
            print("Branch: dealer blackjack")
            self.balance -= self.player_bet
            self._end_round("Dealer has Blackjack! You lose.")
        elif player_blackjack:
            print("Branch: player blackjack")
            self.balance += int(self.player_bet * 1.5)
            self._end_round(f"Blackjack! You win x1.5 ({int(self.player_bet * 1.5)}) your bet!")
        elif self.check_for_bust(self.player_hand):
            print("Branch: player bust")
            self.balance -= self.player_bet
            self._end_round("You Busted!")
        elif self.check_for_bust(self.dealer_hand):
            print("Branch: dealer bust")
            self.balance += self.player_bet
            self._end_round("Dealer Busted!")
        elif self.calculate_hand_value(self.player_hand) == 21:
            print("Branch: auto-stand")
            self._stand()
        #if original two cards are 9,10,11 offer double down
        elif len(self.player_hand) == 2 and self.calculate_hand_value(self.player_hand) in [9,10,11]:
            print("Branch: double down option - enabling double down")
            self.double_down_button.grid(row=0, column=2, padx=10)  # Show double down button
        else:
            print("Branch: normal play - enabling hit/stand")
            self._set_button_states(hit=tk.NORMAL, stand=tk.NORMAL, bet=tk.DISABLED)

    def what_does_the_dealer_have(self):
        if int(self.dealer_hand[0].split("_")[0]) == 14:
            self.deal_score_label.config(text="Dealer's Score: 1/11 + ?")
        else:
            self.deal_score_label.config(text=f"Dealer's Score: {self.calculate_hand_value([self.dealer_hand[0]])} + ?")

    # ------------------------------------------------------------------
    #  Bet Validation                                             
    # ------------------------------------------------------------------ 
    def validate_bet(self, bet):
        if bet.isdigit() or bet == "":
            return True
        return False
    
    # ------------------------------------------------------------------
    #  Image loading                                                    
    # ------------------------------------------------------------------ 
    def get_card_image(self, card_string):
        #Load and return a PhotoImage for the given card string
        #The cards must be named like "2_of_hearts.png", "11_of_clubs.png", etc. in the Card_Images folder
        #11=Jack, 12=Queen, 13=King, 14=Ace
        if card_string in self.card_images:
            return self.card_images[card_string]

        image = Image.open(f'./Card_Images/{card_string}.png')
        image = image.resize((self.card_width, self.card_height)) #resize to fit canvas
        photo = ImageTk.PhotoImage(image)

        self.card_images[card_string] = photo  # Prevent garbage collection
        return photo 
    # ------------------------------------------------------------------
    #  Game actions/Commands                                                   
    # ------------------------------------------------------------------ 
    def _deal(self):
        #Reset hands and deck for a new round
        self.player_hand = []
        self.dealer_hand = []
        # Deal two cards each, alternating like a real deal
        self.player_hand.append(self.draw_from_deck())
        self.dealer_hand.append(self.draw_from_deck())
        self.player_hand.append(self.draw_from_deck())
        self.dealer_hand.append(self.draw_from_deck())
        # Render — dealer's second card is hidden
        self.render_hand(self.player_canvas, self.player_hand)
        self.render_hand(self.dealer_canvas, self.dealer_hand, hide_second=True)

        self.round_result_label.config(text="")
        self.player_score_label.config(text=f"Your Score: {self.calculate_hand_value(self.player_hand)}")
        self.root.title(f"BlackJack Game — {len(self.deck)} cards remaining") #remove once final game is ready
        self.what_does_the_dealer_have()
        self.check_hand_status()

    def _hit(self):
        #Deal one card to the player
        card = self.draw_from_deck()
        self.player_hand.append(card)
        self.render_hand(self.player_canvas, self.player_hand)
        self.player_score_label.config(text=f"Your Score: {self.calculate_hand_value(self.player_hand)}")
        self.root.title(f"BlackJack Game — {len(self.deck)} cards remaining") #remove once final game is ready
        self.check_hand_status()

    def _stand(self):
        #Player stands — reveal dealer's hidden card
        self.render_hand(self.dealer_canvas, self.dealer_hand, hide_second=False)
        self._set_button_states(hit=tk.DISABLED, stand=tk.DISABLED, bet=tk.NORMAL)

        while self.calculate_hand_value(self.dealer_hand) < 17:
            card = self.draw_from_deck()
            self.dealer_hand.append(card)
            self.render_hand(self.dealer_canvas, self.dealer_hand, hide_second=False)
        if self.check_for_bust(self.dealer_hand):
            self.round_result_label.config(text="Round Result:\nDealer Busted! You win!")
            self.deal_score_label.config(text=f"Dealer's Score: {self.calculate_hand_value(self.dealer_hand)}")
            self.balance += self.player_bet  # Add winnings to balance
            self.balance_label.config(text=f"Balance: ${self.balance}")
            return
        self.who_won()
        self.deal_score_label.config(text=f"Dealer's Score: {self.calculate_hand_value(self.dealer_hand)}")

    def _set_button_states(self, hit, stand, bet):
        self.hit_button.config(state=hit)
        self.stand_button.config(state=stand)
        self.place_bet_button.config(state=bet)

    def _end_round(self, message):
        self.round_result_label.config(text=f"Round Result:\n{message}")
        self.render_hand(self.dealer_canvas, self.dealer_hand, hide_second=False)
        self.deal_score_label.config(text=f"Dealer's Score: {self.calculate_hand_value(self.dealer_hand)}")
        self._set_button_states(hit=tk.DISABLED, stand=tk.DISABLED, bet=tk.NORMAL)
        self.balance_label.config(text=f"Balance: ${self.balance}")
        self.bet_message_label.config(text="")

    def _place_bet(self):
        try:
            bet = int(self.bet_entry.get())
            if bet <= 0:
                self.bet_message_label.config(text="Bet must be greater than 0.")
            elif bet > self.balance:
                self.bet_message_label.config(text="Bet exceeds your balance.")
            else:
                self.player_bet = bet
                self.bet_message_label.config(text=f"Bet of ${bet} placed.")
                self._deal()  # Start the round immediately after placing a bet
        except ValueError:
            self.bet_message_label.config(text="Invalid bet amount.")
    
    def _double_down(self):
        self.player_bet *= 2
        self.bet_message_label.config(text=f"Bet doubled to ${self.player_bet}")
        self.double_down_button.grid_forget()
        self._hit()  # Player gets one more card
        self._stand()

    # ------------------------------------------------------------------
    #  Drawing cards and hands                                                   
    # ------------------------------------------------------------------
    def draw_card(self, canvas, x, y, card_string):
        #Draw a face-up card image onto the canvas at position (x, y)
        photo = self.get_card_image(card_string)
        canvas.create_image(x, y, anchor="nw", image=photo)

    def draw_card_back(self, canvas, x, y):
        #Draw a face-down card
        photo = self.get_card_image("card back black")
        canvas.create_image(x, y, anchor="nw", image=photo)

    def render_hand(self, canvas, hand, hide_second=False):
        #Clear the canvas and redraw all cards in a hand
        canvas.delete("all")
        spacing = self.card_width + 10
        for i, card in enumerate(hand):
            x = 10 + i * spacing
            if hide_second and i == 1:
                self.draw_card_back(canvas, x, y=10)
            else:
                self.draw_card(canvas, x, y=10, card_string=card)

    # ------------------------------------------------------------------
    #  UI Layout and Initialization                                                  
    # ------------------------------------------------------------------
    def _build_layout(self):
        # Dealer frame
        self.dealer_frame = tk.Frame(self.root, bg=self.background_color)
        self.dealer_frame.pack(pady=20)

        self.deal_label = tk.Label(
            self.dealer_frame,
            text="Dealer's Hand",
            font=(self.font, 14, "bold"),
            bg=self.background_color,
            fg="white"
        )
        self.deal_label.pack()

        self.deal_score_label = tk.Label(
            self.dealer_frame,
            font=(self.font, 14, "bold"),
            bg=self.background_color,
            fg="white"

        )
        self.deal_score_label.pack()

        self.dealer_canvas = tk.Canvas(
            self.dealer_frame,
            width=700,
            height=120,
            bg=self.background_color,
            highlightthickness=0
        )
        self.dealer_canvas.pack()

        #Player frame
        self.player_frame = tk.Frame(self.root, bg=self.background_color)
        self.player_frame.pack(pady=20)

        self.player_label = tk.Label(
            self.player_frame,
            text="Your Hand",
            font=(self.font, 14, "bold"),
            bg=self.background_color,
            fg="white"
        )
        self.player_label.pack()

        self.player_score_label = tk.Label(
            self.player_frame,
            font=(self.font, 14, "bold"),
            bg=self.background_color,
            fg="white"
        )
        self.player_score_label.pack()

        self.player_canvas = tk.Canvas(
            self.player_frame,
            width=600,
            height=120,
            bg=self.background_color,
            highlightthickness=0
        )
        self.player_canvas.pack()

        self.round_result_label = tk.Label(
            self.player_frame,
            font=(self.font, 14, "bold"),
            bg=self.background_color,
            fg="white"
        )
        self.round_result_label.pack()

        #Button frame
        self.button_frame = tk.Frame(self.root, bg=self.background_color)
        self.button_frame.pack(pady=10)

        self.hit_button = tk.Button(
            self.button_frame,
            text="Hit",
            font=(self.font, self.btn_font_size),
            width=10,
            state=tk.DISABLED,  # Greyed out until game starts
            command=self._hit
        )
        self.hit_button.grid(row=0, column=0, padx=10)

        self.stand_button = tk.Button(
            self.button_frame,
            text="Stand",
            font=(self.font, self.btn_font_size),
            width=10,
            state=tk.DISABLED,
            command=self._stand
        )
        self.stand_button.grid(row=0, column=1, padx=10)

        self.double_down_button = tk.Button(
            self.button_frame,
            text="Double Down",
            font=(self.font, self.btn_font_size),
            width=12,
            command=self._double_down
        )
        self.double_down_button.grid(row=0, column=2, padx=10)
        self.double_down_button.grid_forget()  # Hide double down button initially


        #Betting Frame
        self.betting_frame = tk.Frame(self.root, bg=self.background_color)
        self.betting_frame.place(x=20, y=450)
        self.balance_label = tk.Label(
            self.betting_frame,
            text=f"Balance: ${self.balance}",
            font=(self.font, 14, "bold"),
            bg=self.background_color,
            fg="white"
        )
        self.balance_label.grid(row=0, column=0, columnspan=2, sticky="w",pady=5)

        self.bet_label = tk.Label(
            self.betting_frame,
            text="Bet Amount:",
            font=(self.font, 12),
            bg=self.background_color,
            fg="white"
        )
        self.bet_label.grid(row=1, column=0, sticky="w")

        self.bet_entry = tk.Entry(
            self.betting_frame,
            font=(self.font, 12),
            width=10,
            validate="key",
            validatecommand=(self.root.register(self.validate_bet), "%P")
        )
        self.bet_entry.grid(row=1, column=1, sticky="w")

        self.place_bet_button = tk.Button(
            self.betting_frame,
            text="Place Bet",
            font=(self.font, self.btn_font_size),
            width=10,
            command=self._place_bet
        )
        self.place_bet_button.grid(row=2, column=0, columnspan=2, pady=5, sticky="w")

        self.bet_message_label = tk.Label(
            self.betting_frame,
            text="",
            font=(self.font, 12, "bold"),
            bg=self.background_color,
            fg="white"
        )
        self.bet_message_label.grid(row=4, column=0, sticky="w")
