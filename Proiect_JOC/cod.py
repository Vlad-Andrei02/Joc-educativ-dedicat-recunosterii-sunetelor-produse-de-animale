# Importam bibliotecile necesare
import pygame
import os
import random
import time

# Initializam pygame
pygame.init()

# Declaram culorile pe care le vom folosi
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GRAY = (150, 150, 150)
GREEN = (0, 255, 0)
RED = (255, 0 , 0)

# Dimensiunile ecranului
WIDTH, HEIGHT = 1200, 800

# Dictionar cu animale, fiecarui animal ii corespunde o imagine si un sunet
animals = {
    "dog": ("dog.jpeg", "dog.wav"),
    "cat": ("cat.jpg", "cat.wav"),
    "cow": ("cow.jpg", "cow.wav"),
    "sheep": ("sheep.jpeg", "sheep.wav"),
    "horse": ("horse.png", "horse.wav"),
    "pig": ("pig.jpg", "pig.mp3"),
    "rooster": ("rooster.jpg", "rooster.mp3"),
    "turkey": ("turkey.jpg", "turkey.mp3")
}

# Incarcam sunetul si imaginea corespunzatoare fiecarui animal
def load_the_animals():
    for name_of_animal in animals:
        try:
            animals[name_of_animal] = (pygame.image.load(animals[name_of_animal][0]), pygame.mixer.Sound(animals[name_of_animal][1]))
        except:
            print(f"Pentru animalul {name_of_animal} nu s-a putut incarca imaginea/sunetul.")   

# Setarile jocului, acestea pot fi modificate de jucator prin intermediul interfetei grafice, aceasta va fi implementata ulterior
settings = {
    "rounds": 5, # Vom putea alege sa jucam intre 1 si 10 runde
    "difficulty": "easy", # Vom putea alege sa jucam pe modul easy, mediu sau hard
    "time_thresholds": {"easy": 3, "medium": 1, "hard": 0.5} # Cu cat dificultatea este mai mare, cu atat va fi greu sa iei o nota mai buna, componenta timp a notei va fi afectata de dificultatea selectata
}

# Variabila globala unde stocam toate notele obtinute de jucator
grades = []

# Functii pentru gestionarea notelor

def save_the_grade(grade):
    # Adaugam nota obtinuta in lista de note
    grades.append(grade)

    # Salvam noua nota in fisieul "grades.txt", unde vom stoca toate notele obtinute de jucator
    with open("grades.txt", "a") as f:
        f.write(f"{grade}\n")

def load_grades():
    # Folosim variabila globala grades in cadrul functiei
    global grades

    # Daca fisierul unde stocam notele exista ("grades.txt"), vom citi notele din fisier si le vom salva in variabila globala
    if os.path.exists("grades.txt"):
        with open("grades.txt", "r") as f:
            grades = [float(line.strip()) for line in f.readlines()]

def get_best_3_grades():
    # Returnam cele mai mari 3 note
    return sorted(grades, reverse=True)[:3]

def get_the_average_grade():
    # Returnam media tuturor notelor obtinute de jucator
    return sum(grades) / len(grades) if grades else 0

# Functii pentru joc

def listening_message(screen):
    # Facem ecranul alb
    screen.fill(WHITE)

    # Cream un obiect de tip font, dimensiunea textutlui va fi 52
    font = pygame.font.Font(None, 52)

    # Cream textul
    text = font.render("Asculta sunetul!", True, BLACK)

    # Pozitionam textul
    text_rect = text.get_rect(center = (WIDTH//2, HEIGHT//2))

    # Desenam textul
    screen.blit(text, text_rect)

    # Actualizam ecranul
    pygame.display.flip()

def show_options(screen, options):
    # Facem ecranul alb
    screen.fill(WHITE)

    # Cream un obiect de tip font, dimensiunea textutlui va fi 52
    font = pygame.font.Font(None, 52)

    # Cream textul
    text = font.render("Alege animalul corect!", True, BLACK)

    # Pozitionam textul
    text_rect = text.get_rect(center = (WIDTH//2, 50))

    # Desenam textul
    screen.blit(text, text_rect)

    # Setam dimensiunea imaginilor
    IMAGE_WIDTH = 200
    IMAGE_HEIGHT = 200

    # Setam spatiul dintre imagini
    spacing = (WIDTH - 3 * IMAGE_WIDTH) // 4

    # Dictionar pentru zonele unde putem apasa cu mouse-ul(pe imagini
    buttons = {}

    # Afisam obtiunile(animalele dintre care putem alege)
    for i, animal in enumerate(options):
        # Calculam pozitia imaginii
        x = spacing + i * (IMAGE_WIDTH + spacing)
        y = HEIGHT // 2 - IMAGE_HEIGHT // 2

        # Redimensionam si afisam imaginea animalului
        img = pygame.transform.scale(animals[animal][0], (IMAGE_WIDTH, IMAGE_HEIGHT))
        screen.blit(img, (x, y))

        # Adaugam zona unde putem apasa cu mouse-ul in dictionar
        buttons[(x, y, x + IMAGE_WIDTH, y + IMAGE_HEIGHT)] = animal

    # Actualizam ecranul
    pygame.display.flip()

    # Returnam butoanele
    return buttons

def calculate_grade(score, total_rounds, response_times):
    # Daca nu ghicim niciun animal sau iesim din joc, primim nota 1
    if not response_times or total_rounds == 0 or score == 0:
        return 1
    
    # Calculam cat la suta din raspunsurile jucatorului sunt corecte
    componenta_corectitudine_raspunsuri = score / total_rounds

    # Calculam timpul mediu de raspuns
    avg_time = sum(response_times) / len(response_times)

    # Obtinem pragul de timp, acesta depinde de dificultatea aleasa de jucator
    threshold = settings["time_thresholds"][settings["difficulty"]]

    # Calculam ponderea din nota corespunzatoare timpului de raspuns
    componenta_timp = max(0, 1 - max(0, (avg_time - threshold)))

    # Calculam nota finala si ne asiguram ca este intre 1 si 10
    final_grade = 5 * componenta_corectitudine_raspunsuri + 5 * componenta_timp
    final_grade = min(10, max(1, final_grade))

    # Rotunjim nota la 2 zecimale daca nu este de tip int
    if final_grade == int(final_grade):
        return int(final_grade)
    else:
        return round(final_grade, 2) if len(str(final_grade).split('.')[1]) > 2 else final_grade
    
# Functia jocului propriu-zis
def play_game(screen):
    # Caption
    pygame.display.set_caption("Joc de recunoastere a sunetelor")

    # Incarcam pentru fiecare animal imaginea si sunetul corespunzator
    load_the_animals()

    # Variabile joc
    score = 0 # Cand incepem jocul, scorul initial este 0
    rounds = settings["rounds"] # Luam numarul de runde alese de jucator
    running = True # Aplicatia ruleaza
    time_of_response = [] # Vom stoca timpul de raspuns corespunzator fiecarei runde a jocului

    for _ in range(rounds):
        if not running:
            break

        # La fiecar runda vom avea 3 optiuni din care putem alege, doar una fiind corecta
        correct_animal = random.choice(list(animals.keys())) # Alegem un animal al carui sunet il vom reda
        options = [correct_animal] + random.sample([a for a in animals if a != correct_animal], 2) # Alegem 3 animale ca optiuni pentru jucator, animalul corect si alte 2 animale random
        random.shuffle(options) # Amestecam optiunile ca raspunsul corect sa nu se afle mereu in acelasi loc

        # La inceputul fiecarei runde vom auzi sunetul facut de un animal
        listening_message(screen) # Afisam mesajul unde ii spunem utilizatorului sa asculte sunetul
        pygame.time.delay(700) # Delay

        # Redam sunetul animalului
        sound = animals[correct_animal][1]
        sound.play()

        # Variabila care ne spune daca sunetul s-a terminat
        sound_is_playing = True

        # Gestionare evenimente in timp ce redam sunetul
        while sound_is_playing:
            for event in pygame.event.get():
                # Gestionare iesire din joc
                if event.type == pygame.QUIT:
                    running = False
                    sound_is_playing  = False

            # Gestionare redare sunet cu succes
            if not pygame.mixer.get_busy():
                sound_is_playing = False

        # Afisam optiunile si asteptam ca jucatorul sa aleaga un animal
        buttons = show_options(screen, options) # Returnam zonele unde putem apasa cu mouse ul in vederea alegerii unui animal
        start_time = time.time() # Pornim cronometrul

        # Variabila care ne spune daca jucatorul a ales un animal
        waiting_choice = True

        # Gestionare evenimente de dupa redarea sunetului
        while waiting_choice and running:
            for event in pygame.event.get():
                # Gestionare iesire din joc
                if event.type == pygame.QUIT:
                    running = False
                    waiting_choice = False

                # Gestionare alegere animal
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Pozitia unde am apasat pe mouse
                    x, y = event.pos

                    # Verificam daca am apasat pe o imagine
                    for(x1, y1, x2, y2), animal in buttons.items():
                        # Gestionam clickul pe o imagine
                        if x1 < x < x2 and y1< y < y2:
                            response_time = time.time() - start_time # Calculam timpul de raspuns
                            time_of_response.append(response_time) # Salvam timpul de raspuns

                            # Daca am raspuns corect, primim un punct
                            if animal == correct_animal:
                                score += 1
                            waiting_choice = False # Nu mai asteptam ca utilizatorul sa aleaga, din moment ce deja am ales
                            break

        pygame.time.delay(500) # Delay

    # Calculam nota
    grade = calculate_grade(score, rounds, time_of_response)
    

    # Salvam nota doar daca jucatorul a terminat jocul(altfel am salva multe note de 1, afectand inutil statisticile)
    if running:
        save_the_grade(grade)

    # Afisam rezultatele

    # Facem ecranul alb
    screen.fill(WHITE)

    # Cream un obiect de tip font, dimensiunea textului va fi de 48
    font = pygame.font.Font(None, 46) # Cream textul

    # Afisare numar de raspunsuri corecte
    text_raspunsuri_corecte = font.render(f"Raspunsuri corecte: {score}/{rounds}", True, BLACK)
    text_raspunsuri_corecte_rect = text_raspunsuri_corecte.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
    screen.blit(text_raspunsuri_corecte, text_raspunsuri_corecte_rect)

    # Afisam nota obtinuta
    text_nota_obtinuta = font.render(f"Nota obtinuta: {grade}", True, BLACK)
    text_nota_obtinuta_rect = text_nota_obtinuta.get_rect(center=(WIDTH//2, HEIGHT//2 ))
    screen.blit(text_nota_obtinuta, text_nota_obtinuta_rect)

    # Afisare mesaj pentru iesire in meniu
    text_exit_menu = font.render("Apasa orice tasta pentru a continua...", True, BLACK)
    text_exit_menu_rect = text_exit_menu.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
    screen.blit(text_exit_menu, text_exit_menu_rect)

    # Actualizam ecranul
    pygame.display.flip()

    # Asteptam input utilizator
    waiting = True
    while waiting:
            for event in pygame.event.get():
                # Gestionare iesire din joc
                if event.type == pygame.QUIT:
                    waiting = False
                    pygame.quit()
                    return

                # Gestionare apasarea oricarui buton(dorinta jucatorului de a se intoarce la meniu)
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    waiting = False

# Functie pentru afisare statistici
def statistics(screen):
    # Caption
    pygame.display.set_caption("Statistici")

    # Facem ecranul alb
    screen.fill(WHITE)

    # Font pentru titlu si statistici
    font_title = pygame.font.Font(None, 70)
    font_statistics = pygame.font.Font(None, 50)

    # Citim notele din fisierul "grades.txt", unde avem stocate toate notele obtinute de jucator
    load_grades()

    # Afisam titlul
    title = font_title.render(f"Statistici", True, BLACK)
    title_rect = title.get_rect(center=(WIDTH//2, 100))
    screen.blit(title, title_rect)

    # Afisam cele mai mare 3 note obtinute de jucator
    top_grades= get_best_3_grades()

    if top_grades:
        top_text = font_statistics.render("Cele mai bune 3 note:", True, BLACK)
        top_rect = top_text.get_rect(center=(WIDTH//2, 200))
        screen.blit(top_text, top_rect)

        for i, grade in enumerate(top_grades):
            grade_text = font_statistics.render(f"{i + 1}. {grade}", True, BLACK)
            grade_rect = grade_text.get_rect(center = (WIDTH//2, 250 + i*50))
            screen.blit(grade_text, grade_rect)
    else:
        no_data = font_statistics.render("Nu exista date statistice", True, BLACK)
        no_rect = no_data.get_rect(center=(WIDTH//2, 250))
        screen.blit(no_data, no_rect)

    # Afisare average grades
    avg_grade = get_the_average_grade()
    avg_text = font_statistics.render(f"Media notelor: {avg_grade:.2f}", True, BLACK)
    avg_rect = avg_text.get_rect(center=(WIDTH//2, 450))
    screen.blit(avg_text, avg_rect)

    # Afisare mesaj in care indrumam utilizatorul sa apese orice tasta pentru a reveni in meniu
    return__to_menu_text = font_statistics.render("Apasa orice tasta pentru a reveni", True, GRAY)
    return_to_menu_rect = return__to_menu_text.get_rect(center=(WIDTH//2, 550))
    screen.blit(return__to_menu_text, return_to_menu_rect)

    # Actualizam ecranul
    pygame.display.flip()

    # Asteptam imput utilizator
    waiting = True
    while waiting:
            for event in pygame.event.get():
                # Gestionare iesire din joc
                if event.type == pygame.QUIT:
                    waiting = False
                    pygame.quit()
                    return

                # Gestionare apasarea oricarui buton(dorinta jucatorului de a se intoarce la meniu)
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    waiting = False

# Functie pentru setari
def show_settings(screen):
    # Caption
    pygame.display.set_caption("Setari")

    # Facem ecranul alb
    screen.fill(WHITE)

    # Fonturi folosite
    font_titlu = pygame.font.Font(None, 70)
    font_mediu = pygame.font.Font(None, 50)
    font_small = pygame.font.Font(None, 35)

    # Afisam titlul
    title = font_titlu.render("Setari", True, BLACK)
    title_rect = title.get_rect(center=(WIDTH//2, 99))
    screen.blit(title, title_rect)

    # Afisam dificultatile pe care le poate alege jucatorul
    diff_text = font_mediu.render("Dificultate:", True, BLACK)
    diff_rect = diff_text.get_rect(center=(WIDTH//2 - 150, 200))
    screen.blit(diff_text, diff_rect) 

    # Butoane dificultate
    easy_rect = pygame.Rect(WIDTH//2 + 50, 180, 120, 50)
    medium_rect = pygame.Rect(WIDTH//2 + 180, 180, 120, 50)
    hard_rect = pygame.Rect(WIDTH//2 + 310, 180, 120, 50)

    # Coloram dificultatea selectata cu albastru, iar pe celelalte cu gri
    colors = {
        "easy": BLUE if settings["difficulty"] == "easy" else GRAY,
        "medium": BLUE if settings["difficulty"] == "medium" else GRAY,
        "hard": BLUE if settings["difficulty"] == "hard" else GRAY,
    } 

    # Desenam butoanele
    pygame.draw.rect(screen, colors["easy"], easy_rect)
    pygame.draw.rect(screen, colors["medium"], medium_rect)
    pygame.draw.rect(screen, colors["hard"], hard_rect)

    # Textul din interiorul butoanelor de selectare a dificultatii
    easy_text = font_small.render("Easy", True, WHITE)
    medium_text = font_small.render("Medium", True, WHITE)
    hard_text = font_small.render("Hard", True, WHITE)

    # Afisam textul in interiorul butoanelor de selectare a dificultatii
    screen.blit(easy_text, (easy_rect.x + 30, easy_rect.y + 15))
    screen.blit(medium_text, (medium_rect.x + 20, easy_rect.y + 15))
    screen.blit(hard_text, (hard_rect.x + 30, hard_rect.y + 15))

    # Optiuni runde
    rounds_text = font_mediu.render("Numar runde:", True, BLACK)
    rounds_Rect = rounds_text.get_rect(center=(WIDTH//2 - 150, 300))
    screen.blit(rounds_text, rounds_Rect)

    # Butoane runde
    minus_rect = pygame.Rect(WIDTH//2 + 50, 280, 50, 50)
    plus_rect = pygame.Rect(WIDTH//2 + 250, 280, 50, 50)
    num_rect = pygame.Rect(WIDTH//2 + 110, 280, 130, 50)
    
    # Desenare butoane
    pygame.draw.rect(screen, GRAY, minus_rect)
    pygame.draw.rect(screen, GRAY, plus_rect)
    pygame.draw.rect(screen, WHITE, num_rect, 2)

    # Textul din interiorul butoanelor de selectare a numarului de runde
    minus_text = font_mediu.render("-", True, BLACK)
    plus_text = font_mediu.render("+", True, BLACK)
    num_text = font_mediu.render(str(settings["rounds"]), True, BLACK)

    # Afisam textul din interiorul butoanelor de selectare a numerului de runde
    screen.blit(minus_text, (minus_rect.x + 20, minus_rect.y + 10))
    screen.blit(plus_text, (plus_rect.x + 15, plus_rect.y + 10))
    screen.blit(num_text, (num_rect.x + 55, num_rect.y + 10))

    # Buton back
    back_rect = pygame.Rect(WIDTH//2 - 100, 400, 200, 60)
    pygame.draw.rect(screen, GRAY, back_rect)
    back_text = font_mediu.render("Inapoi", True, BLACK)
    screen.blit(back_text, (back_rect.x + 50, back_rect.y + 15))

    # Actualizam ecranul
    pygame.display.flip()

    # Asteptam imput utilizator
    waiting = True
    while waiting:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            # Gestionare iesire din joc
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                return

            # Gestionare schimbare dificultate, numar runde si intoarcere la meniu 
            if event.type == pygame.MOUSEBUTTONDOWN:
                 # Schimbam dificultatea daca jucatorul a selectat o alta dificultate
                if easy_rect.collidepoint(mouse_pos):
                    settings["difficulty"] = "easy"
                    
                elif medium_rect.collidepoint(mouse_pos):
                    settings["difficulty"] = "medium"

                elif hard_rect.collidepoint(mouse_pos):
                    settings["difficulty"] = "hard"
                    
                # Schimbam numarul de runde, scazand cu 1 la fiecare apasare a butonului - cat timp numarul de runde este mai mare decat 1
                elif minus_rect.collidepoint(mouse_pos) and settings["rounds"] > 1:
                    # Scadem numarul de runde la apasarea butonului
                    settings["rounds"] -= 1

                    # Stergem vechea valoare
                    pygame.draw.rect(screen, WHITE, num_rect)

                    # Adaugam noua valoare
                    num_text = font_mediu.render(str(settings["rounds"]), True, BLACK)

                # Schimbam numarul de runde, adaugand 1 la fiecare apasare a butonului + cat timp numarul de runde este mai mic decat 10
                elif plus_rect.collidepoint(mouse_pos) and settings["rounds"] < 10:
                    # Adaugam numarul de runde la apasarea butonului
                    settings["rounds"] += 1

                    # Stergem vechea valoare
                    pygame.draw.rect(screen, WHITE, num_rect)

                    # Adaugam noua valoare
                    num_text = font_mediu.render(str(settings["rounds"]), True, BLACK)

                    # Daca apasam pe butonul back revenim la meniu
                elif back_rect.collidepoint(mouse_pos):
                    waiting = False

        # Schimbam culoarea butoanelor la hover
        colors = {
            "easy": GREEN if easy_rect.collidepoint(mouse_pos) else (BLUE if settings["difficulty"] == "easy" else GRAY),
            "medium": GREEN if medium_rect.collidepoint(mouse_pos) else (BLUE if settings["difficulty"] == "medium" else GRAY),        
            "hard": GREEN if hard_rect.collidepoint(mouse_pos) else (BLUE if settings["difficulty"] == "hard" else GRAY),
            "minus": RED if minus_rect.collidepoint(mouse_pos) else GRAY,
            "plus": GREEN if plus_rect.collidepoint(mouse_pos) else GRAY,
            "back": RED if back_rect.collidepoint(mouse_pos) else GRAY
        }

        # Desenam butoanele
        pygame.draw.rect(screen, colors["easy"], easy_rect)
        pygame.draw.rect(screen, colors["medium"], medium_rect)
        pygame.draw.rect(screen, colors["hard"], hard_rect)
        pygame.draw.rect(screen, colors["minus"], minus_rect)            
        pygame.draw.rect(screen, colors["plus"], plus_rect)
        pygame.draw.rect(screen, colors["back"], back_rect)

        # Redesenam textul
        screen.blit(easy_text, (easy_rect.x + 30, easy_rect.y + 15))
        screen.blit(medium_text, (medium_rect.x + 20, medium_rect.y + 15))
        screen.blit(hard_text, (hard_rect.x + 30, easy_rect.y + 15))                
        screen.blit(minus_text, (minus_rect.x + 20, minus_rect.y + 8))
        screen.blit(plus_text, (plus_rect.x + 15, plus_rect.y + 5))
        screen.blit(num_text, (num_rect.x + 55, num_rect.y + 10))
        screen.blit(back_text, (back_rect.x + 50, back_rect.y + 15))

        # Actualizam ecranul
        pygame.display.update()

# Meniu principal
def main_menu():
    # Display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Caption
    pygame.display.set_caption("Meniu")

    # Adaugare poza background, in caz ca nu gaseste poza backgroundul va fi verde
    try:
        BG = pygame.transform.scale(pygame.image.load("poza_background.jpg"), (WIDTH, HEIGHT))
    except:
        BG = pygame.Surface((WIDTH, HEIGHT))
        BG.fill(GREEN)

    # Font optiuni
    font = pygame.font.Font(None, 65)

    # Dimensiunea butoanelor si spatiere
    BUTTON_WIDTH = 175
    BUTTON_HEIGHT = 55
    SPACING = 20
    OFFSET_X = 355
    button_x = (WIDTH - BUTTON_WIDTH) // 2 - OFFSET_X
    start_y = (HEIGHT - (3 * BUTTON_HEIGHT + 2 * SPACING)) // 2

    # Hit boxul butoanelor
    button_hitboxes = {
        "Start": pygame.Rect(button_x, start_y, BUTTON_WIDTH, BUTTON_HEIGHT),
        "Setari": pygame.Rect(button_x, start_y + BUTTON_HEIGHT + SPACING, BUTTON_WIDTH, BUTTON_HEIGHT),
        "Statistici": pygame.Rect(button_x, start_y + 2 * (BUTTON_HEIGHT + SPACING), BUTTON_WIDTH, BUTTON_HEIGHT)
    }

    # Transformare cursor arrow in cursor mana cand mouse ul se afla pe unul dintre cele 3 hitboxuri
    cursor_hand = pygame.SYSTEM_CURSOR_HAND
    cursor_arrow = pygame.SYSTEM_CURSOR_ARROW
    pygame.mouse.set_cursor(cursor_arrow)

    # While loop principal al jocului
    run = True
    while run:
        # Desenam fundalul
        screen.blit(BG, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        hover = False # Indicator prezenta mouse pe unul dintre butoane

        # Desenare butoane
        for text, rect in button_hitboxes.items():
            # Afisare text in buton
            label = font.render(text, True, WHITE)

            # Centrare text in buton
            screen.blit(label, (rect.x + (BUTTON_WIDTH - label.get_width()) // 2, rect.y + (BUTTON_HEIGHT - label.get_height()) // 2))

            # Verificam prezenta mouse_ului peste buton
            if rect.collidepoint(mouse_pos):
                hover = True

        # Schimba cursorul la mana daca se afla peeste buton
        if hover:
            pygame.mouse.set_cursor(cursor_hand)
        else:
            pygame.mouse.set_cursor(cursor_arrow)

        # Gestionare evenimente
        for event in pygame.event.get():
            # Iesire joc
            if event.type == pygame.QUIT:
                run = False

            # Apasare butoane
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for text, rect in button_hitboxes.items():
                    if rect.collidepoint(mouse_pos):
                        # Apasare start
                        if text == "Start":
                            # Apelare functie de incepere a jocului
                            play_game(screen)

                            # Resetare ecran
                            screen= pygame.display.set_mode((WIDTH, HEIGHT))

                            # Setare caption inapoi la meniu
                            pygame.display.set_caption("Meniu")

                        # Apasare setari
                        elif text == "Setari":
                            # Apelare functie de setari
                            show_settings(screen)

                            # Resetare ecran
                            screen = pygame.display.set_mode((WIDTH, HEIGHT))

                            # Setare caption inapoi la meniu
                            pygame.display.set_caption("Meniu")

                        # Apasare statistici
                        elif text == "Statistici":
                            # Apelare functie de statistici
                            statistics(screen)

                            # Resetare ecran
                            screen = pygame.display.set_mode((WIDTH, HEIGHT))

                            # Setare caption inapoi la meniu
                            pygame.display.set_caption("Meniu")

        #Actualizare ecran
        pygame.display.update()

    # Inchidem Pygame la iesire
    pygame.quit()

# Punct de intrare al jocului
if __name__ == "__main__":
    main_menu()

        



