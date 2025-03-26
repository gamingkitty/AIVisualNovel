import scene
import sys
import pygame
import text
import option
import ollama
import re
import ast


def get_deepseek_response(
    user_prompt: str,
    model: str = "deepseek-r1:7b"
) -> str:
    # Get raw response
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )["message"]["content"]

    # Remove <think>...</think> tags
    cleaned = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<think>", "", cleaned, flags=re.IGNORECASE)
    print(cleaned)

    # Look for code block marked with ```python or '''python
    match = re.search(r"(?:```|''')python\s+(.*?)(?:```|''')", cleaned, flags=re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()
    else:
        return cleaned.strip()


def make_options(option_texts, option_background, screen_size):
    options = []
    option_x = screen_size[0] / 2
    option_y = 50

    for option_text in option_texts:
        current_option = option.Option(option_text, option_background, (option_x, option_y))
        option_y += option_background.get_height() + 50
        options.append(current_option)

    return options


def get_response(style, previous_scene, chosen_option):
    prompt = f'''
You are a professional storyteller you must create a story about {style}. You will tell from the main character's perspective as if the user is in the story. You will tell each story in separate scenes. Each scene will have a description of the scene as an image. You will also tell the story and provide options for the user to select. then in following prompts use the option to continue the scenes. You will also be provided with data about the last scene and the text of the last scene.
 
if no option and scene description provided assume it is the beginning of the story
 
you will return your answer as a python list.
 
Here is an example:
 
Story about a silly clown
 
Example:
 
Input:
[["You are a clown with a red nose.", "You are very hungry", "You go into the fridge and select a food item to eat"], ["cheese", "peanuts", "milk"], "photo of a fridge"]
 
Output:
 
[["You just woke up and you wanted to do something"], ["Get out of bed", "Stay In Bed"], "photo of a bed"]
 
Return scene description lines like this ["I jumped", "I ran"]
Return options like this: ["hide","sleep"]
 
Dont modify the formatting of your answer only return how the examples show
 
 
the first is the description for the scene where each element int he array is a line then is the option you can have as many as you want limit it from 2 - 5. 3rd is a description of the image. 2nd to last is the previous option and the last is the previous scene text  


This is the previous scene in the story. You will have to continue off the story from here based on what option the player chose to do.
Previous scene: {previous_scene}
Option chosen by player: {chosen_option}
 
 
ONLY RETURN THE PYTHON DATA ONLY
'''
    return ast.literal_eval(get_deepseek_response(prompt))


def main():
    pygame.init()
    pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT, pygame.KEYUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("AI Thing")

    fps = 60
    clock = pygame.time.Clock()

    screen_size = screen.get_size()
    screen_width = screen_size[0]
    screen_height = screen_size[1]

    text_box_img = pygame.image.load("Text Box.png")
    text_box_img = pygame.transform.scale(text_box_img, (600, 300))
    text_box = text.Text("text", text_box_img, ((screen_width - text_box_img.get_width()) / 2, screen_height - text_box_img.get_height() - 30))
    response = [["W-where am I?", "Why am I surrounded by dark figures...", "I need to do something."], ["Run", "Fight", "Cower"], "A dark scene with dark figures hovering over the camera."]

    background = pygame.Surface(screen_size)
    background.fill((0, 0, 0))

    option_background = pygame.image.load("Option Background.png")
    option_background = pygame.transform.scale(option_background, (option_background.get_width() * 2, option_background.get_height() * 2))

    current_scene = scene.Scene(response[0], text_box, background, make_options(response[1], option_background, screen_size))
    while True:
        delta_time = clock.tick(fps) / 1000

        current_scene.load(screen)
        current_scene.move(delta_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    current_scene.handle_mouse_down()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    current_scene.handle_mouse_up()

        if current_scene.get_chosen_option() is not None:
            chosen_option_text = current_scene.get_chosen_option().get_text()
            response = get_response("Horror", response, chosen_option_text)
            current_scene = scene.Scene(response[0], text_box, background, make_options(response[1], option_background, screen_size))

        pygame.display.flip()


if __name__ == "__main__":
    main()
