#from tkinter import *
#from tkinter import ttk
import tkinter as tk
import random
from PIL import Image, ImageTk

class BlackJackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BlackJack Game")
        self.root.geometry("800x600")
        self.root.resizable(width=False, height=False)
        self.root.configure(bg="#076324") # casino green background
        self.font = "Courier New"
        self.btn_font_size = 12
        self.card_font_size = 11
        self.background_color = "#076324"
        self.card_width = 70
        self.card_height = 100

        self.card_images = {}  # Cache for card images to prevent garbage collection
        self.deck = []  # Will hold the current deck of cards
        self.player_hand = []  # List to hold player's cards
        self.dealer_hand = []  # List to hold dealer's cards

        self.make_deck()  # Initialize the deck of cards
        self._build_layout()
    # ------------------------------------------------------------------
    #  Deck                                                   
    # ------------------------------------------------------------------ 
    def make_deck(self):
        suits = ["hearts", "diamonds", "clubs", "spades"]
        rank = range(2, 15) # 11=Jack, 12=Queen, 13=King, 14=Ace
        for _ in range(6):  # Increase to 6 for a shoe of 6 decks  
            for suit in suits:
                for r in rank:
                    self.deck.append(f"{r}_of_{suit}")

    def draw_from_deck(self):
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
            temp_value = value + 11 + (aces - 1)  # One Ace as 11, rest as 1
            if temp_value > 21:
                value += aces  # All Aces as 1
            else:
                value += 11 + (aces - 1)  # One Ace as 11, rest as 1
        elif aces == 1:
            if value + 11 > 21:
                value += 1  # Ace as 1
            else:
                value += 11  # Ace as 11
        return value
    
    def check_for_bust(self, hand):
        if self.calculate_hand_value(hand) > 21:
            self.render_hand(self.dealer_canvas, self.dealer_hand, hide_second=False)
            self.player_score_label.config(text=f"Your Score: {self.calculate_hand_value(self.player_hand)}")
            self.deal_score_label.config(text=f"Dealer's Score: {self.calculate_hand_value(self.dealer_hand)}")
            self.hit_button.config(state=tk.DISABLED)
            self.stand_button.config(state=tk.DISABLED)
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
        elif dealer_score == player_score:
            self.round_result_label.config(text="Round Result:\nIt's a Tie!")
        else:
            self.round_result_label.config(text="Round Result:\nDealer wins!")

    def check_hand_status(self):
        #Both have blackjack
        if self.check_blackjack(self.dealer_hand) and self.check_blackjack(self.player_hand):
            self.round_result_label.config(text="Round Result:\nStand-off. Bets returned!")
            self.hit_button.config(state=tk.DISABLED)
            self.stand_button.config(state=tk.DISABLED)
            self.render_hand(self.dealer_canvas, self.dealer_hand, hide_second=False)
        #Dealer has blackjack
        elif self.check_blackjack(self.dealer_hand):
            self.round_result_label.config(text="Round Result:\nDealer has Blackjack! You lose.")
            self.hit_button.config(state=tk.DISABLED)
            self.stand_button.config(state=tk.DISABLED)
            self.render_hand(self.dealer_canvas, self.dealer_hand, hide_second=False)
        #Player has blackjack
        elif self.check_blackjack(self.player_hand):
            self.round_result_label.config(text="Round Result:\nBlackjack! You win x1.5 your bet!")
            self.hit_button.config(state=tk.DISABLED)
            self.stand_button.config(state=tk.DISABLED)
            self.render_hand(self.dealer_canvas, self.dealer_hand, hide_second=False)
        #Nobody has blackjack, check for busts
        elif self.check_for_bust(self.player_hand):
            self.round_result_label.config(text="Round Result:\nYou Busted!")
            self.hit_button.config(state=tk.DISABLED)
            self.stand_button.config(state=tk.DISABLED)
            self.deal_button.config(state=tk.NORMAL)
        elif self.check_for_bust(self.dealer_hand):
            self.round_result_label.config(text="Round Result:\nDealer Busted!")
            self.hit_button.config(state=tk.DISABLED)
            self.stand_button.config(state=tk.DISABLED)
            self.deal_button.config(state=tk.NORMAL)
        #Auto-stand on 21
        elif self.calculate_hand_value(self.player_hand) == 21:
            self._stand()
        else:
            self.hit_button.config(state=tk.NORMAL)
            self.stand_button.config(state=tk.NORMAL)
            self.deal_button.config(state=tk.DISABLED)
    def what_does_the_dealer_have(self):
        if int(self.dealer_hand[0].split("_")[0]) == 14:
            self.deal_score_label.config(text="Dealer's Score: 1/11 + ?")
        else:
            self.deal_score_label.config(text=f"Dealer's Score: {self.calculate_hand_value([self.dealer_hand[0]])} + ?")

    # ------------------------------------------------------------------
    #  Image loading                                                    
    # ------------------------------------------------------------------ 
    def get_card_image(self, card_string):
        #Load and return a PhotoImage for the given card string
        if card_string in self.card_images:
            return self.card_images[card_string]

        image = Image.open(f'./Card_Images/{card_string}.png')
        image = image.resize((self.card_width, self.card_height)) #resize to fit canvas
        photo = ImageTk.PhotoImage(image)

        self.card_images[card_string] = photo  # Prevent garbage collection
        return photo 
           
    def draw_card_back(self, canvas, x, y):
        #Draw a face-down card
        photo = self.get_card_image("card back black")  # Expects ./Card_Images/back.png
        canvas.create_image(x, y, anchor="nw", image=photo)

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

        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)

        # Render — dealer's second card is hidden
        self.render_hand(self.player_canvas, self.player_hand)
        self.render_hand(self.dealer_canvas, self.dealer_hand, hide_second=True)
       
        #self.deal_score_label.config(text="")
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
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)
        self.deal_button.config(state=tk.NORMAL)

        while self.calculate_hand_value(self.dealer_hand) < 17:
            card = self.draw_from_deck()
            self.dealer_hand.append(card)
            self.render_hand(self.dealer_canvas, self.dealer_hand, hide_second=False)
        if self.check_for_bust(self.dealer_hand):
            self.round_result_label.config(text="Round Result:\nDealer Busted! You win!")
            self.deal_score_label.config(text=f"Dealer's Score: {self.calculate_hand_value(self.dealer_hand)}")
            return
        self.who_won()
        self.deal_score_label.config(text=f"Dealer's Score: {self.calculate_hand_value(self.dealer_hand)}")

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

        #Button frame
        self.button_frame = tk.Frame(self.root, bg=self.background_color)
        self.button_frame.pack(pady=10)

        self.deal_button = tk.Button(
            self.button_frame,
            text="Deal",
            font=(self.font, self.btn_font_size),
            width=10,
            command=self._deal
        )
        self.deal_button.grid(row=0, column=0, padx=10)

        self.hit_button = tk.Button(
            self.button_frame,
            text="Hit",
            font=(self.font, self.btn_font_size),
            width=10,
            state=tk.DISABLED,  # Greyed out until game starts
            command=self._hit
        )
        self.hit_button.grid(row=0, column=1, padx=10)

        self.stand_button = tk.Button(
            self.button_frame,
            text="Stand",
            font=(self.font, self.btn_font_size),
            width=10,
            state=tk.DISABLED,
            command=self._stand
        )
        self.stand_button.grid(row=0, column=2, padx=10)


        #Betting Frame
        self.betting_frame = tk.Frame(self.root, bg=self.background_color)
        self.betting_frame.pack(pady=20)

        self.round_result_label = tk.Label(
            self.betting_frame,
            font=(self.font, 14, "bold"),
            bg=self.background_color,
            fg="white"
        )
        self.round_result_label.pack()
