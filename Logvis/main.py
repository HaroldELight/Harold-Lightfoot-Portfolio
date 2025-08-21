from config import settings
from ai.brain import Brain
from memory.memory import Memory

def main():
    brain = Brain()
    memory = Memory()
    print("Welcome to Logvis! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = brain.chat(user_input, memory)
        print("AI:", response)

if __name__ == "__main__":
    main()
