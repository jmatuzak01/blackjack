from tkinter import *
import random
from PIL import Image, ImageTk

root = Tk()
root.title("Test drawing cards")
#root.iconbitmap("icon.ico")
root.geometry("900x500")
root.config(bg="green")

def resize_cards(card):
    our_card_img = Image.open(card)
    resized_card = our_card_img.resize((150, 218))
    # output the card
    global our_card_image
    our_card_image = ImageTk.PhotoImage(resized_card)
    return our_card_image

def shuffle():
    suits = ["hearts", "diamonds", "clubs", "spades"]
    rank = range(2, 15)

    global deck
    deck = []
    for _ in range(6):    
        for suit in suits:
            for r in rank:
                deck.append(f"{r}_of_{suit}")
    global dealer, player
    dealer = []
    player = []

    card = random.choice(deck)
    deck.remove(card)

    dealer.append(card)

    global dealer_image
    dealer_image = resize_cards(f'./Card_Images/{card}.png')

    dealer_label.config(image=dealer_image)

    card = random.choice(deck)
    deck.remove(card)

    player.append(card)

    global player_image
    player_image = resize_cards(f'./Card_Images/{card}.png')

    player_label.config(image=player_image)

    root.title(f"Test drawing cards - {len(deck)} cards left in deck")

def deal_cards():
    try:
        card = random.choice(deck)
        deck.remove(card)

        dealer.append(card)

        global dealer_image
        dealer_image = resize_cards(f'./Card_Images/{card}.png')

        dealer_label.config(image=dealer_image)

        card = random.choice(deck)
        deck.remove(card)

        player.append(card)

        global player_image
        player_image = resize_cards(f'./Card_Images/{card}.png')

        player_label.config(image=player_image)

        root.title(f"Test drawing cards - {len(deck)} cards left in deck")
    except:
        root.title("Test drawing cards - No more cards in deck")

my_frame = Frame(root, bg="green")
my_frame.pack(pady=20)

dealer_frame = LabelFrame(my_frame, text="Dealer", bd=0)
dealer_frame.grid(row=0, column=0, padx=20, ipadx=20)

player_frame = LabelFrame(my_frame, text="Player", bd=0)
player_frame.grid(row=0, column=1, padx=20, ipadx=20)

dealer_label = Label(dealer_frame, text='')
dealer_label.pack(pady=20)

player_label = Label(player_frame, text='')
player_label.pack(pady=20)

shuffle_button = Button(root, text="Shuffle Deck", font=("Helvetica", 14), command=shuffle)
shuffle_button.pack(pady=20)

card_button = Button(root, text="Draw Card", font=("Helvetica", 14),command=deal_cards)
card_button.pack(pady=20)

shuffle()
root.mainloop()