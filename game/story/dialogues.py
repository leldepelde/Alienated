
def _tier(char_id, high=30, mid=15):
    def pick(s):
        r = s.rel(char_id)
        return "high" if r >= high else "mid" if r >= mid else "low"
    return pick

DIALOGUES = {
    # =================================================================== VERA
        "vera_intro": {
            "start": {
                "speaker": "vera", "mood": "neutral",
                "text": "Hey, you're up! So glad you could join us! I'm Vera, the captain. "
                        "Over in that room is Rex, the engineer. And you're our linguist!",
                "next": "cv",
            },
            "cv": {
                "speaker": "vera", "mood": "neutral",
                "text": "I mean, your CV was unlike any other applicant. An alien linguist "
                        "and a rocket scientist? Do you know how rare that is?",
                "next": "ask",
            },
            "ask": {
                "speaker": "vera", "mood": "neutral",
                "text": "So! Nine days to Mars. Earth stopped answering our calls, and "
                        "the Martians are doing... whatever it is they're doing. How are "
                        "you feeling?",
                "choices": [
                    {"text": "Totally ready. This is what I trained for.",
                     "goto": "bluff", "affect": {"vera": +4}},
                    {"text": "Actually I'm a little terrified.",
                     "goto": "honest", "affect": {"vera": +8}},
                    {"text": "About that CV... I may have exaggerated.",
                     "goto": "confess", "affect": {"vera": +5}},
                ],
            },
            "bluff": {
                "speaker": "vera", "mood": "happy",
                "text": "That's the spirit! I was worried you'd be all serious and scientific",
                "set_flags": ["bluffed_vera"],
                "next": "outro",
            },
            "honest": {
                "speaker": "vera", "mood": "happy",
                "text": "Oh, thank goodness. Me too! Everyone else pretends they're fine "
                        "and it's exhausting. We're going to get along great.",
                "next": "outro",
            },
            "confess": {
                "speaker": "vera", "mood": "happy",
                "text": "Ha! That's so funny, ha ha, no need to be so humble!",
                "set_flags": ["confessed_vera"],
                "next": "confess2",
            },
            "confess2": {
                "speaker": "vera", "mood": "neutral",
                "text": "Seriously though, we are so glad to have you and your skills.",
                "next": "outro",
            },
            "outro": {
                "speaker": "vera", "mood": "happy",
                "text": "Go say hi to Rex! He pretends he isn't nervous, but he's "
                        "reorganized the toolbox four times today.",
            },
        },
        "vera_after_console": {   
            "start": {
                "speaker": "vera", "mood": "neutral",
                "text": "AAAAA WHATS HAPPENING?!",
                "next": lambda s: "fixed" if "console_fixed" in s.flags else "failed",
            },
            "fixed": {
                "speaker": "vera", "mood": "happy",
                "affect": {"vera": +5},
                "text": "What is that noise I hear? A working engine? No wayyy!!!",
                "choices": [
                    {"text": "Putting those rocket scientist skills to use...hahahaha",
                    "goto": "unsure", "affect": {"vera": -5}},
                    {"text": "Wow you're so excited! How many of those snack boxes did you have?",
                    "goto": "insecure", "affect": {"vera": -10}},
                    {"text": "Yea, I'm suprised that actually worked!",
                    "goto": "yay", "affect": {"vera": +5}},
                ],
                },
                "unsure":{
                    "speaker": "vera", "mood": "netural",
                    "text": "Yea, good for you! Just so you know this ship already has an engineer...",
                },
                "insecure":{
                    "speaker": "vera", "mood":"angry",
                    "text": "Hahahaha, don't worry about that.",
                },
                "yay":{
                    "speaker": "vera", "mood":"happy",
                    "text": "Awww, don't doubt yourself!"
                            "You're probably the smartest of us all",
                },
            "failed": {
                "speaker": "vera", "mood": "angry",
                "affect" : {"vera": -10},
                "text": "WHAT THE FLIP!!! Why did you ruin our perfectly good engine?!?!"
                        "GO BACK AND FIX ITTTTT!",
                } 
            },
        "vera_invasion_signal": {   
                    "start": {
                        "speaker": "vera", "mood": "neutral",
                        "text": "Do you think the signal went through?",
                        "next": lambda s: "decoded" if "signal_decoded" in s.flags else "failed",
                    },
                    "decoded":{
                        "speaker": "vera", "mood": "neutral",
                        "text": "OH MYYYY GAWDDD",
                        "next": "what",
                    },
                    "what":{
                        "speaker": "vera", "mood": "angry",
                        "text": "How did YOU get in here?!?!?",
                        "next": "aaalien",
                    },
                    "aaalien":{
                        "speaker": "alien", "mood": "neutral",
                        "text": "~ZEEPY ZOOPY~",
                        "next": "rexcomes"
                    },
                    "rexcomes":{
                        "speaker": "rex", "mood": "neutral",
                        "text": "I heard a loud sound, did something happen?",
                        "next": "ohmy",
                    },
                    "ohmy":{
                        "speaker": "rex", "mood" : "angry",
                        "text": "Oh cool, hahahaha. An alien in our ship, that's so chill.",
                        "next":"poop",
                    },
                    "poop":{
                        "speaker": "rex", "mood":"neutral",
                        "text": "*poops a little*",
                        "next":"movingon",
                    },
                    "movingon":{
                        "speaker": "alien", "mood":"neutral",
                        "text":"Dance",
                    },
                    "failed":{
                        "speaker": "rex", "mood":"angry",
                        "text": "No, it didn't... Go try again alien linguist."
                    }
        },
        "vera_chat": {
            "start": {
                "speaker": "vera", "mood": "happy",
                "text": "Oh, hey! Need something?",
                "next": lambda s: ("confessed" if "confessed_vera" in s.flags
                                   else _tier("vera")(s)),
            },
            "confessed": {
                "speaker": "vera", "mood": "happy",
                "text": "Still thinking about that CV joke, by the way. 'I may have "
                        "exaggerated.' Classic. So, what's up?",
                "next": "menu",
            },
            "high": {
                "speaker": "vera", "mood": "happy",
                "text": "My favorite linguist! I saved you the good snacks. What's up?",
                "next": "menu",
            },
            "mid": {
                "speaker": "vera", "mood": "neutral",
                "text": "Hey! Everything okay? What's up?",
                "next": "menu",
            },
            "low": {
                "speaker": "vera", "mood": "neutral",
                "text": "Oh. Hi. Is this about the mission? What's up?",
                "next": "menu",
            },
            "menu": {
                "speaker": "vera", "mood": "neutral",
                "text": "Ask me anything. Except about the weird noise in the vents. "
                        "Rex already told me. Twice.",
                "choices": [
                    {"text": "What do we actually know about the Martians?",
                     "goto": "martians"},
                    {"text": "What's the plan when we land?", "goto": "plan"},
                    {"text": "Do you ever get scared?", "goto": "scared",
                     "affect": {"vera": +2}},
                    {"text": "Nothing, just saying hi.", "goto": "hi"},
                ],
            },
            "martians": {
                "speaker": "vera", "mood": "neutral",
                "text": "Well? Not much. Just strange signals."
                  "That's why we need you. The one person who "
                        "can actually read them!",
                "next": "martians2",
            },
            "martians2": {
                "speaker": "vera", "mood": "happy",
                "text": "No pressure though! I'm sure it's mostly just 'hello' and "
                        "'please stop attacking us.'",
            },
            "plan": {
                "speaker": "vera", "mood": "angry",
                "text": "Land, make contact, you do your linguist thing, Rex keeps the "
                        "engines warm. I'll smile and nod a lot. It's a "
                        "great plan.",
            },
            "scared": {
                "speaker": "vera", "mood": "angry",
                "text": "Constantly! But try not think about it too much. "
                        "I packed an alarming number of snacks to cope.",
            },
            "hi": {
                "speaker": "vera", "mood": "happy",
                "text": "Hi! Hi hi hi. Okay, I'm glad you came by.",
            },
        },
    
        # ========================================================================================================== REX
        "rex_intro": {
            "start": {
                "speaker": "rex", "mood": "neutral",
                "text": "Oh. Hey. You're the linguist. Cool. I'm Rex. "
                        "Engineer. I fix things. It's whatever.",
                "next": "calm",
            },
            "calm": {
                "speaker": "rex", "mood": "neutral",
                "text": "I'm totally calm, by the way. This is just my face. Anyway, "
                        "the engine console keeps glitching. You're a rocket scientist, "
                        "right? Could you take a look?",
                "next": "ask",
            },
            "ask": {
                "speaker": "rex", "mood": "neutral",
                "text": "It goes way easier if I'm helping. Not that I need help. I just "
                        "like... being nearby. For safety. Not mine.",
                "choices": [
                    {"text": "Sure! Rocket science is basically my middle name.",
                     "goto": "bluff", "affect": {"rex": +5}},
                    {"text": "Sorry, not really my area. I'm more of a words person.",
                     "goto": "honest", "affect": {"rex": +2}},
                    {"text": "Rex, are you okay? You look pale.",
                     "goto": "confide", "affect": {"rex": +8}},
                    {"text": "Isn't that your job?",
                     "goto": "ouch", "affect": {"rex": -4}},
                ],
            },
            "bluff": {
                "speaker": "rex", "mood": "happy",
                "text": "Oh, cool. I mean, obviously. Of course you are. "
                        "Vera said you were top of your class. At everything.",
                "set_flags": ["bluffed_rex"],
                "next": "outro",
            },
            "honest": {
                "speaker": "rex", "mood": "angry",
                "text": "Huh. Funny, Vera said you were both. Never mind! You're just "
                        "being modest. Of course.",
                "next": "outro",
            },
            "confide": {
                "speaker": "rex", "mood": "angry",
                "text": "Pale? No. This is my normal color. ...Okay, I haven't slept in "
                        "a bit. But it's nothing."
                        "It's definitely nothing.",
                "set_flags": ["rex_confided"],
                "next": "confide2",
            },
            "confide2": {
                "speaker": "rex", "mood": "happy",
                "text": "Thanks for asking, though. Nobody asks the engineer how he's "
                        "doing. They just ask what's broken.",
                "next": "outro",
            },
            "ouch": {
                "speaker": "rex", "mood": "angry",
                "text": "Wow. Okay. Fine. It is my job. Cool, whatever. "
                "*wipes sweat bead off forhead*",
                "next": "outro",
            },
            "outro": {
                "speaker": "rex", "mood": "neutral",
                "text": "Console's in the engine room, bottom left. If it makes a "
                        "beeping noise, don't panic. It's nothing. *gulp*",
            },
        },

            "rex_after_console": {
        "start": {
            "speaker": "rex", "mood": "neutral",
            "text": "Oh did something happen? I thought I heard something..",
            "next": lambda s: "fixed" if "console_fixed" in s.flags else "failed",
        },
        "fixed": {
            "speaker": "rex", "mood": "happy",
            "text": "You got the engine up again, that's cool or whatever",
            "affect": {"rex": +5},
            "choices":[
                {"text": "Yea! I don't know how you built that thing, it's so detailed",
                 "goto": "compliment", "affect": {"rex": +5}},
                {"text": "Yeaa, it was quite simple, I'm suprised you missed it."
                "Yikes...",
                "goto": "offend", "affect" : {"rex": -7}},
            ],
        },
        "compliment":{
            "speaker": "rex", "mood":"happy",
            "text": "Thank you..or whatever"
            "*starts fidgeting*",
        },
        "offend":{
            "speaker":"rex", "mood":"angry",
            "text": "Okay cool, I don't even care hahaha ",
            "next": "sadvibe",
        },
        "sadvibe":{
            "speaker":"rex", "mood":"neutral",
            "text":"*wipes tear off cheek*",
        },
        "failed": {
            "speaker": "rex", "mood": "angry",
            "text": "Dude, why did the lights go out?",
            "next":"mad",
        },
        "mad":{
            "speaker": "rex", "mood": "neutral",
            "text": "Okay it's no big deal, just go fix it please. I'm panicking? No YOU'RE panicking hahahaha..."
        },
    },
    "rex_invasion_signal": {   
            "start": {
                "speaker": "rex", "mood": "neutral",
                    "text": "Oh hey. You just tried to send the signal right? Hmm let's see if it worked..",
                    "next": lambda s: "decoded" if "signal_decoded" in s.flags else "failed",
            },
                "decoded":{
                "speaker": "rex", "mood": "neutral",
                "text": "What was that!",
                "next": "what",
                        },
                "what":{
                "speaker": "rex", "mood": "angry",
                "text": "no no no NO NO NO "
                "THAT'S IT, BYE",
                "next": "run",
                    },
                "run":{
                    "speaker": "vera", "mood": "angry",
                    "text": "Did I just see Rex jump out the spaceship? What is going on?!",
                    "next":"aaalien",
                },
                "aaalien":{
                    "speaker": "alien", "mood": "neutral",
                    "text": "~ZEEPY ZOOPY~",
                    "next": "verascared",
                        },
                "verascared":{
                    "speaker": "vera", "mood": "neutral",
                    "text": "OH FLIPPPP! Okay it's your time to shine linguist! "
                    "Talk to him!!!",
                    "choices":[
                        {"text": "Ermmm....hey, mr. alien..?",
                         "goto": "madalin"},
                        {"text": "ZORP ZORP ZORP",
                         "goto": "madalin"},
                    ],
                },
                "madalin":{
                    "speaker": "alien", "mood":"neutral",
                    "text":"Dance",
                        },
                "failed":{
                    "speaker": "rex", "mood":"angry",
                    "text": "No, it didn't... Go try again alien linguist."
                        }
            },
    
        "rex_chat": {
            "start": {
                "speaker": "rex", "mood": "neutral",
                "text": "Oh! Yo. I wasn't hiding. I was inspecting.. this.",
                "next": lambda s: ("confided" if "rex_confided" in s.flags
                                   else _tier("rex")(s)),
            },
            "confided": {
                "speaker": "rex", "mood": "happy",
                "text": "Hey, it's you. The one who asked. Thanks again.",
                "next": "menu",
            },
            "high": {
                "speaker": "rex", "mood": "happy",
                "text": "Oh good, a familiar face. I'm glad that you're here. Not that I "
                        "was scared. I just like company.",
                "next": "menu",
            },
            "mid": {
                "speaker": "rex", "mood": "neutral",
                "text": "Hey. Need anything? I mean, I can help. If it's quick. And "
                        "not near the vents. *scratches head*",
                "next": "menu",
            },
            "low": {
                "speaker": "rex", "mood": "angry",
                "text": "Oh. It's you. Is something broken? Please say no.",
                "next": "menu",
            },
            "menu": {
                "speaker": "rex", "mood": "neutral",
                "text": "So. What do you need or whatever?",
                "choices": [
                    {"text": "How's the engine looking?", "goto": "engine"},
                    {"text": "Did you hear a noise just now?", "goto": "noise"},
                    {"text": "Why did you want to go to Mars anyway?", "goto": "mars",
                     "affect": {"rex": +2}},
                    {"text": "Nothing. Just checking in.", "goto": "bye"},
                ],
            },
            "engine": {
                "speaker": "rex", "mood": "neutral",
                "text": "Fine. It's fine. It makes a sound I don't recognize, but "
                        "that's probably normal. You'd know. Rocket scientist.",
            },
            "noise": {
                "speaker": "rex", "mood": "angry",
                "text": "It's just the ship settling. I think. *deep breath* Ships "
                        "settle. Or maybe turbulence. I'm going to go stand over there.",
            },
            "mars": {
                "speaker": "rex", "mood": "happy",
                "text": "Well... I wanted to see something nobody has seen. I just "
                        "didn't think it might see me back.",
            },
            "bye": {
                "speaker": "rex", "mood": "happy",
                "text": "Oh. Okay. That's... nice. Thanks. Don't tell Vera I said that.",
            },
        },
} #YEEEEEHAW BABY