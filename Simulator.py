import pygame

class Mirror: #A mirror that reflects all radiation. It does not emit or absorb radiation.
    
    def __init__(self, simulation): #We need the position of the mirror, a reference to the simulation object.
        self.simulation = simulation #A reference to the simulation object, so the mirror can access the screen and other objects.
        self.simulation.slots.append(self) #Add this mirror to the simulation's list of objects to draw and update.

    def draw(self): #Draw the mirror as a gray rectangle.
        color = (200, 200, 200) #Gray color for the mirror.
        font = pygame.font.SysFont('arialblack', 12) #Create a font object with the specified font and size.
        wind = pygame.display.get_window_size()
        pygame.draw.rect(self.simulation.screen, color, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1), 10, 10, 150)) #Draw a rectangle at (x, y) with width and height of 10 pixels.
        img = font.render(f"Mirror", True, color) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) - 50, 200)) #Draw the temperature text next to the blackbody.
    
    def emit_radiation(self): #Mirrors do not emit radiation.
        pass

    def absorb_radiation(self): #Mirrors do not absorb radiation.
        pass

class HeatSource: #A heat source (blackbody) that is supplied a constant amount of heat (in Watts), has a temperature, and emits and absorbs radiation.
    
    def __init__(self, simulation, watts=400, temperature=0, specific_heat=1, mass=1): #We need the position of the blackbody, a reference to the simulation object. optional physical properties.
        self.watts = watts #In Watts (Joules per second)
        self.simulation = simulation #A reference to the simulation object, so the blackbody can access the screen and other objects.
        self.temperature = temperature #In Kelvin
        self.specific_heat = specific_heat #In J/(kg*K)
        self.mass = mass #In kg
        self.simulation.slots.append(self) #Add this blackbody to the simulation's list of objects to draw and update.
        self.incoming_radiation_left = 0 #In Watts (Joules per second).
        self.incoming_radiation_right = 0 #In Watts (Joules per second).

    def draw(self): #Draw the heat source as a rectangle. Color depends on temperature.
        font = pygame.font.SysFont('arialblack', 12) #Create a font object with the specified font and size.
        color_value = min(255, max(0, int(self.temperature*.5))) #Map temperature to a color value between 0 and 255
        color = (color_value, 0, 255 - color_value) #Color shifts from blue (cold) to red (hot)
        pygame.draw.rect(self.simulation.screen, color, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1), 10, 10, 150)) #Draw a rectangle at (x, y) with width and height of 10 pixels.
        img = font.render(f"{self.temperature:.2f} K", True, color) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) - 50, 220)) #Draw the temperature text next to the blackbody.
        img = font.render(f"Heatsource {self.watts}W", True, color) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) - 50, 200)) #Draw the temperature text next to the blackbody.
        img = font.render(f"{self.calc_watts():.2f}W <->", True, color) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) - 60, 175)) #Draw the temperature text next to the blackbody.

    def calc_watts(self): #Calculate the power emitted by the blackbody using the Stefan-Boltzmann law. We are simulating one milisecond, so Watts/1000 = Joules.
        SB_CONSTANT = 5.67e-8 # Stefan-Boltzmann constant in W/m^2K^4
        return SB_CONSTANT * self.temperature**4 # Power emitted per unit area
    
    def emit_radiation(self): #Mirrors do not emit radiation.
        SB_CONSTANT = 5.67e-8 # Stefan-Boltzmann constant in W/m^2K^4
        emission = SB_CONSTANT / 1000 * self.temperature**4 # Power emitted per unit area
        index = self.simulation.slots.index(self) #Find the index of this object in the simulation's list of objects.
        if index - 1 < 0: #If there is no object to the left...
            self.simulation.JoulesLostToSpace += emission #...then we lose the radiation to space.
        else:
            if isinstance(self.simulation.slots[index - 1], Mirror): #If the object to the left is a mirror...
                self.incoming_radiation_right += emission #Emit radiation leftward, bounces off a mirror, and is saved as rightward incoming radiation back into this object. 
            else: 
                self.simulation.slots[index - 1].incoming_radiation_right += emission #Send radiation to the previous (left) object in the list.
        if  index + 1 > len(self.simulation.slots) - 1: #If there is no object to the right...
            self.simulation.JoulesLostToSpace += emission #...then we lose the radiation to space.
        else:
            if isinstance(self.simulation.slots[index + 1], Mirror): #If the object to the right is a mirror...
                self.incoming_radiation_left += emission #Emit radiation rightward, bounces off a mirror, and is saved as leftward incoming radiation back into this object. 
            else:
                self.simulation.slots[index + 1].incoming_radiation_left += emission #Send radiation to the next (right) object in the list.
        delta_temp = emission*2 / (self.mass * self.specific_heat) # ΔT = Q / (m*c), with 2x because we emit in two directions.
        self.temperature -= delta_temp #Lose temperature due to radiation emission.s
        if self.temperature < 0: #Clamp temperature to 0K. Shold never happen, but needed for simulation stability.
            self.temperature = 0

    def absorb_radiation(self): #Absorb incoming radiation and update temperature.
        radiation = self.incoming_radiation_left + self.incoming_radiation_right + self.watts/1000 #Add the constant heat input in Joules (Watts/1000 for miliseconds)
        if radiation > 0: #If there is any incoming radiation...
            delta_temp = radiation / (self.mass * self.specific_heat) # ΔT = Q / (m*c)
            self.temperature += delta_temp #Increase temperature due to absorbed radiation.
            self.incoming_radiation_left = 0 #Reset incoming radiation after absorption.
            self.incoming_radiation_right = 0 #Reset incoming radiation after absorption.

class Blackbody: #A blackbody that emits and absorbs radiation.
    
    def __init__(self, simulation, temperature=0, specific_heat=1, mass=1): #We need the position of the blackbody, a reference to the simulation object. optional physical properties.
        self.simulation = simulation #A reference to the simulation object, so the blackbody can access the screen and other objects.
        self.temperature = temperature #In Kelvin
        self.specific_heat = specific_heat #In J/(kg*K)
        self.mass = mass #In kg
        self.simulation.slots.append(self) #Add this blackbody to the simulation's list of objects to draw and update.
        self.incoming_radiation_left = 0 #In Watts (Joules per second).
        self.incoming_radiation_right = 0 #In Watts (Joules per second).

    def draw(self): #Draw the blackbody as a rectangle. Color depends on temperature.
        font = pygame.font.SysFont('arialblack', 12) #Create a font object with the specified font and size.
        color_value = min(255, max(0, int(self.temperature*.5))) #Map temperature to a color value between 0 and 255
        color = (color_value, 0, 255 - color_value) #Color shifts from blue (cold) to red (hot)
        pygame.draw.rect(self.simulation.screen, color, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1), 10, 10, 150)) #Draw a rectangle at (x, y) with width and height of 10 pixels.
        img = font.render(f"{self.temperature:.2f} K", True, color) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) - 50, 220)) #Draw the temperature text next to the blackbody.
        img = font.render(f"Blackbody", True, color) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) - 50, 200)) #Draw the temperature text next to the blackbody.
        img = font.render(f"{self.calc_watts():.2f}W <->", True, color) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) - 60, 175)) #Draw the temperature text next to the blackbody.

    def calc_watts(self): #Calculate the power emitted by the blackbody using the Stefan-Boltzmann law. We are simulating one milisecond, so Watts/1000 = Joules.
        SB_CONSTANT = 5.67e-8 # Stefan-Boltzmann constant in W/m^2K^4
        return SB_CONSTANT * self.temperature**4 # Power emitted per unit area

    def emit_radiation(self): #Calculate the power emitted by the blackbody using the Stefan-Boltzmann law. We are simulating one milisecond, so Watts/1000 = Joules.
        SB_CONSTANT = 5.67e-8 # Stefan-Boltzmann constant in W/m^2K^4
        emission = SB_CONSTANT / 1000 * self.temperature**4 # Power emitted per unit area
        index = self.simulation.slots.index(self) #Find the index of this object in the simulation's list of objects.
        if index - 1 < 0: #If there is no object to the left...
            self.simulation.JoulesLostToSpace += emission #...then we lose the radiation to space.
        else:
            if isinstance(self.simulation.slots[index - 1], Mirror): #If the object to the left is a mirror...s
                self.incoming_radiation_left += emission #Emit radiation leftward, bounces off a mirror, and is saved as rightward incoming radiation back into this object. 
            else:
                self.simulation.slots[index - 1].incoming_radiation_right += emission #Send radiation to the previous (left) object in the list.
        if  index + 1 > len(self.simulation.slots) - 1: #If there is no object to the right...
            self.simulation.JoulesLostToSpace += emission #...then we lose the radiation to space.
        else:
            if isinstance(self.simulation.slots[index + 1], Mirror): #If the object to the right is a mirror...
                self.incoming_radiation_right += emission #Emit radiation rightward, bounces off a mirror, and is saved as leftward incoming radiation back into this object. 
            else:
                self.simulation.slots[index + 1].incoming_radiation_left += emission #Send radiation to the next (right) object in the list.
        delta_temp = emission*2 / (self.mass * self.specific_heat) # ΔT = Q / (m*c), with 2x because we emit in two directions.
        self.temperature -= delta_temp #Lose temperature due to radiation emission.
        if self.temperature < 0: #Clamp temperature to 0K. Shold never happen, but needed for simulation stability.
            self.temperature = 0
        
    def absorb_radiation(self): #Absorb incoming radiation and update temperature.
        radiation = self.incoming_radiation_left + self.incoming_radiation_right #Total incoming radiation in Watts (Joules per second).
        if radiation > 0: #If there is any incoming radiation...
            delta_temp = radiation / (self.mass * self.specific_heat) # ΔT = Q / (m*c)
            self.temperature += delta_temp #Increase temperature due to absorbed radiation.
            self.incoming_radiation_left = 0 #Reset incoming radiation after absorption.
            self.incoming_radiation_right = 0 #Reset incoming radiation after absorption.

class TwoSidedBlackbody: #A blackbody that emits and absorbs radiation separately on its left and right sides, and conducts heat between its two sides.
    
    def __init__(self, simulation, temperature_left=0, temperature_right=0, specific_heat_left=1, specific_heat_right = 1, mass_left=0.5, mass_right=0.5, width=1, conductivity=5, area=1): #We need the position of the blackbody, a reference to the simulation object. optional physical properties.
        self.simulation = simulation #A reference to the simulation object, so the blackbody can access the screen and other objects.
        self.temperature_left = temperature_left #In Kelvin
        self.area = area #In square meters. Area through which heat conducts.
        self.temperature_right = temperature_right #In Kelvin
        self.specific_heat_left = specific_heat_left #In J/(kg*K)
        self.specific_heat_right = specific_heat_right #In J/(kg*K)
        self.mass_right = mass_right #In kg 
        self.mass_left = mass_left #In kg
        self.width = width #In meters. (defined from the center of the left side to the center of the right side)
        self.conductivity = conductivity #In W/(m*K). How well heat conducts through the material.
        self.simulation.slots.append(self) #Add this blackbody to the simulation's list of objects to draw and update.
        self.incoming_radiation_left = 0 #In Watts (Joules per second).
        self.incoming_radiation_right = 0 #In Watts (Joules per second).

    def draw(self): #Draw the blackbody as a rectangle. Color depends on temperature.
        font = pygame.font.SysFont('arialblack', 12) #Create a font object with the specified font and size.
        color_value_left = min(255, max(0, int(self.temperature_left*.5))) #Map temperature to a color value between 0 and 255
        color_value_right = min(255, max(0, int(self.temperature_right*.5))) #Map temperature to a color value between 0 and 255
        color_left = (color_value_left, 0, 255 - color_value_left) #Color shifts from blue (cold) to red (hot)
        color_right = (color_value_right, 0, 255 - color_value_right) #Color shifts from blue (cold) to red (hot)
        pygame.draw.rect(self.simulation.screen, color_left, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1), 10, 5, 150)) #Draw a rectangle at (x, y) with width and height of 10 pixels.
        pygame.draw.rect(self.simulation.screen, color_right, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) + 5, 10, 5, 150)) #Draw a rectangle at (x, y) with width and height of 10 pixels.
        img = font.render(f"{self.temperature_left:.2f} K left", True, color_left) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) - 50, 220)) #Draw the temperature text next to the blackbody.
        img = font.render(f"{self.temperature_right:.2f} K right", True, color_right) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) - 50, 240)) #Draw the temperature text next to the blackbody.
        img = font.render(f"TwoSided", True, color_left) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) - 85, 200)) #Draw the temperature text next to the blackbody.
        img = font.render(f"BBody", True, color_right) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) , 200)) #Draw the temperature text next to the blackbody.
        img = font.render(f"{self.calc_watts("left"):.2f}W <-", True, color_left) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) - 90, 175)) #Draw the temperature text next to the blackbody.
        img = font.render(f"{self.calc_watts("right"):.2f}W ->", True, color_right) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1), 175)) #Draw the temperature text next to the blackbody.

    def calc_watts(self, side): #Calculate the power emitted by the blackbody using the Stefan-Boltzmann law. We are simulating one milisecond, so Watts/1000 = Joules.
        if side == "left":
            temperature = self.temperature_left
        else:
            temperature = self.temperature_right
        SB_CONSTANT = 5.67e-8 # Stefan-Boltzmann constant in W/m^2K^4
        return SB_CONSTANT * temperature**4 # Power emitted per unit area

    def emit_radiation(self): #Calculate the power emitted by the blackbody using the Stefan-Boltzmann law. We are simulating one milisecond, so Watts/1000 = Joules.
        SB_CONSTANT = 5.67e-8 # Stefan-Boltzmann constant in W/m^2K^4
        emission_left = SB_CONSTANT / 1000 * self.temperature_left**4 # Power emitted per unit area
        emission_right = SB_CONSTANT / 1000 * self.temperature_right**4 # Power emitted per unit area
        index = self.simulation.slots.index(self) #Find the index of this object in the simulation's list of objects.
        if index - 1 < 0: #If there is no object to the left...
            self.simulation.JoulesLostToSpace += emission_left #...then we lose the radiation to space.
        else:
            if isinstance(self.simulation.slots[index - 1], Mirror): #If the object to the left is a mirror...s
                self.incoming_radiation_left += emission_left #Emit radiation leftward, bounces off a mirror, and is saved as rightward incoming radiation back into this object. 
            else:
                self.simulation.slots[index - 1].incoming_radiation_right += emission_left #Send radiation to the previous (left) object in the list.
        if  index + 1 > len(self.simulation.slots) - 1: #If there is no object to the right...
            self.simulation.JoulesLostToSpace += emission_right #...then we lose the radiation to space.
        else:
            if isinstance(self.simulation.slots[index + 1], Mirror): #If the object to the right is a mirror...
                self.incoming_radiation_right += emission_right #Emit radiation rightward, bounces off a mirror, and is saved as leftward incoming radiation back into this object. 
            else:
                self.simulation.slots[index + 1].incoming_radiation_left += emission_right #Send radiation to the next (right) object in the list.
        delta_temp_left = emission_left / (self.mass_left * self.specific_heat_left) # ΔT = Q / (m*c), with 2x because we emit in two directions.
        self.temperature_left -= delta_temp_left #Lose temperature due to radiation emission.
        if self.temperature_left < 0: #Clamp temperature to 0K. Shold never happen, but needed for simulation stability.
            self.temperature_left = 0
        delta_temp_right = emission_right / (self.mass_right * self.specific_heat_right) # ΔT = Q / (m*c), with 2x because we emit in two directions.
        self.temperature_right -= delta_temp_right #Lose temperature due to radiation emission.     
        if self.temperature_right < 0: #Clamp temperature to 0K. Shold never happen, but needed for simulation stability.
            self.temperature_right = 0  
        
    def absorb_radiation(self): #Absorb incoming radiation and update temperature.
        if self.incoming_radiation_left > 0: #If there is any incoming radiation...
            delta_temp = self.incoming_radiation_left / (self.mass_left * self.specific_heat_left) # ΔT = Q / (m*c)
            self.temperature_left += delta_temp #Increase temperature due to absorbed radiation.
            self.incoming_radiation_left = 0 #Reset incoming radiation after absorption.
        if self.incoming_radiation_right > 0: #If there is any incoming radiation...
            delta_temp = self.incoming_radiation_right / (self.mass_right * self.specific_heat_right) # ΔT = Q / (m*c)
            self.temperature_right += delta_temp #Increase temperature due to absorbed radiation.
            self.incoming_radiation_right = 0 #Reset incoming radiation after absorption.

    def conduct(self): #Conduct heat between the two sides of the blackbody.
        delta_temp = self.temperature_right - self.temperature_left #Temperature difference between the two sides.
        if delta_temp != 0: #If there is a temperature difference...
            heat_transfer = self.conductivity * self.area * delta_temp / self.width / 1000 # Q = k*A*ΔT/d, with A=width*1m (1m depth into the screen), d=width
            delta_temp_left = heat_transfer / (self.mass_left * self.specific_heat_left) # ΔT = Q / (m*c)
            delta_temp_right = heat_transfer / (self.mass_right * self.specific_heat_right) # ΔT = Q / (m*c)
            self.temperature_left += delta_temp_left #Increase temperature on the left side.
            self.temperature_right -= delta_temp_right #Decrease temperature on the right side.
            if self.temperature_left < 0: #Clamp temperature to 0K. Should never happen, but needed for simulation stability.
                self.temperature_left = 0
            if self.temperature_right < 0: #Clamp temperature to 0K. Should never happen, but needed for simulation stability.
                self.temperature_right = 0

class Void: #A void that does not emit or have a temperature, but can absorb radiation and remove it from the system.:
    
    def __init__(self, simulation): #We need the position of the void, a reference to the simulation object.
        self.simulation = simulation #A reference to the simulation object, so the void can access the screen and other objects.
        self.simulation.slots.append(self) #Add this void to the simulation's list of objects to draw and update.
        self.incoming_radiation_left = 0 #In Watts (Joules per second).
        self.incoming_radiation_right = 0 #In Watts (Joules per second).

    def draw(self): #Draw the mirror as a gray rectangle.
        color = (255, 255, 255) #Gray color for the mirror.
        font = pygame.font.SysFont('arialblack', 12) #Create a font object with the specified font and size.
        wind = pygame.display.get_window_size()
        pygame.draw.rect(self.simulation.screen, color, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1), 10, 10, 150), width=2) #Draw a rectangle at (x, y) with width and height of 10 pixels.
        img = font.render(f"Void", True, color) #Render the temperature text.
        self.simulation.screen.blit(img, ((self.simulation.slots.index(self) + 1)*pygame.display.get_window_size()[0]/(len(self.simulation.slots) + 1) - 50, 200)) #Draw the temperature text next to the blackbody.
    
    def emit_radiation(self): #Mirrors do not emit radiation.
        pass

    def absorb_radiation(self): #Mirrors do not absorb radiation.
        absorbed = self.incoming_radiation_left + self.incoming_radiation_right
        self.simulation.JoulesLostToSpace += absorbed #All absorbed radiation is lost to space.
        self.incoming_radiation_left = 0 #Reset incoming radiation after absorption.
        self.incoming_radiation_right = 0 #Reset incoming radiation after absorption.=

class Simulation: #This is the main class. It contains all the code for running the simulation.

    def __init__(self): #Constructor for the Simulation object. This code gets run whenever we make a new Simulation object, like: Simulation(). 
            self.screen = pygame.display.set_mode((1500, 400)) #Sets the size of the display in terms of number of pixels. Width, then height.
            self.clock = pygame.time.Clock() #Starts the gameclock, which sets the speed of the simulation.
            self.running = True #A variable we can use a switch to shut the Simulation off if we need to.
            self.slots = [] #A list to hold all of our blackbody objects, mirrors, and heat sources. Order of creation determines order of the ojects in space
            self.JoulesLostToSpace = 0 #A variable to keep track of how much energy has been lost to space over the course of the simulation.
            self.prevJoulesLostToSpace = 0 #A variable to keep track of how much energy has been lost to space in the previous mili-second of the simulation.

    def draw(self): #A method Games can do. It draws everything that should be on the screen to the screen, then updates the screen.
            self.screen.fill((0, 0, 0)) #black out the screen. This removes the last drawing we made, so we start with a fresh black canvas.
            for object in self.slots: #For each object in our list of objects...
                object.draw() #Tell that object to draw itself.
            font = pygame.font.SysFont('arialblack', 15) #Create a font object with the specified font and size.
            watts_in = sum([obj.watts for obj in self.slots if isinstance(obj, HeatSource)]) #Calculate total watts input from all heat sources.
            img = font.render(f"Lost to space: {self.JoulesLostToSpace:.2f} J, Watts to space: {(self.JoulesLostToSpace-self.prevJoulesLostToSpace)*1000:.2f} W, System:  {self.calc_energy():.2f} J, Watts to System: {watts_in} W,  Total: {self.JoulesLostToSpace + self.calc_energy():.2f}", True, (255, 255, 255)) #Render the temperature text.
            self.screen.blit(img, (10, 300))
            self.prevJoulesLostToSpace = self.JoulesLostToSpace #Save the current Joules lost to space for the next update cycle.
            pygame.display.update() #Update the screen to show the new drawing.

    def events(self): #When called, Simulation checks if any input (clicking the x button, hitting a specific key, etc) needs acting on, and acts on it.
        for event in pygame.event.get(): #For each event pygame has as occuring...
            if event.type == pygame.QUIT: #If that event is the type of event that comes when the user hits the x button....
                self.running=False #Flips our switch to stop running the simulation. This closes the simulation, and the window.

    def update(self): #Anything that changes in the simulation, happens here.  
        for object in self.slots: #For each object in our list of objects...
            object.emit_radiation() #Tell that object to emit radiation.
        for object in self.slots: #For each object in our list of objects...
            if isinstance(object, TwoSidedBlackbody): #Only TwoSidedBlackbodies conduct heat between their two sides.
                object.conduct() #Tell that object to conduct heat between its two sides.
        for object in self.slots: #For each object in our list of objects...
            object.absorb_radiation() #Tell that object to absorb radiation.
            
    def create(self): #This method sets up the initial state of the simulation. It is called once at the start of the simulation.

        #Blackbody(self) creates a blackbody object. It absorbs all radiation, and emits according to the SB law. It has a temperature, mass, and specific heat
        #TwoSidedBlackbody(self) creates a blackbody object with two sides that can have different temperatures. It absorbs all radiation, and emits according to the SB law. It has a temperature, mass, and specific heat for each side, and conductivity between the two sides.
        #HeatSource(self) creates a blackbody object that is supplied a constant amount of heat (in Watts), and is otherwise identical to a blackbody.
        #Mirror(self) creates a mirror object. It reflects all radiation, and does not have a temperature, mass, or specific heat.
        #Void(self) creates a void object. It absorbs all radiation, but does not emit any radiation, and does not have a temperature, mass, or specific heat.

        #All objects are placed in a line, in the order they are created. The first object is on the left, the last object is on the right.


        #This setup creates the Eli Rabbet thought experiment with the single plate setup on the left and the two plate setup on the right. 
        

        #HeatSource(self)
        #Void(self)
        #HeatSource(self)
        #Blackbody(self)


        #This setup creates your experiment, with a mirror and 6 blackbodies. 

        #Mirror(self)
        #Blackbody(self, temperature=500)
        #Blackbody(self, temperature=500)
        #Blackbody(self, temperature=500)
        #Blackbody(self, temperature=500)
        #Blackbody(self, temperature=500)
        #Blackbody(self, temperature=500)


        #Simulations worth running for theory reasons. pt. 1: isolated system

        #Mirror(self)
        #Blackbody(self, temperature=500)
        #Blackbody(self, temperature=500)
        #Mirror(self)

      

        #Simulations worth running for theory reasons. pt. 2: room temperature using a mirror. Everything --hot or cold-- should go to room temperature.

        #Mirror(self)
        #Blackbody(self, temperature=500)
        #Blackbody(self, temperature=0)
        #HeatSource(self)


        #Pictet's experiment simulation setup pt 1: room temperature with no mirrors, and a thermal reservoir to keep room temp constant.

        #HeatSource(self, watts=200, temperature=243.7, mass=1000000)
        #Blackbody(self, temperature=243.7)
        #Blackbody(self, temperature=243.7)
        #HeatSource(self, watts=200, temperature=243.7, mass=1000000)

        #Pictet's experiment simulation setup pt 2: placing a hot object in our room, next to another blackbody, which is our 'thermometer'.

        #HeatSource(self, watts=200, temperature=243.7, mass=1000000)
        #Blackbody(self, temperature=500)
        #Blackbody(self, temperature=243.7)
        #HeatSource(self, watts=200, temperature=243.7, mass=1000000)

        #Pictet's experiment simulation setup pt 3: placing a COLD object in our room, next to another blackbody, which is our 'thermometer'.

        #HeatSource(self, watts=200, temperature=243.7, mass=1000000)
        #Blackbody(self, temperature=0)
        #Blackbody(self, temperature=243.7)
        #HeatSource(self, watts=200, temperature=243.7, mass=1000000)



        #A side by side comparison of the two sided blackbodies and single sided blackbodies.
       
        TwoSidedBlackbody(self, conductivity=1.5) 
        TwoSidedBlackbody(self, conductivity=1.5) 
        HeatSource(self)
        Mirror(self)
        HeatSource(self)
        Blackbody(self)
        Blackbody(self)
        
    def calc_energy(self): #A method to calculate the total energy in the system. 
        total_energy = 0 #Start with zero energy.
        for object in self.slots: #For each object in our list of objects...
            if isinstance(object, Blackbody) or isinstance(object, HeatSource): #Only blackbodies and heat sources have thermal energy.
                total_energy += object.mass * object.specific_heat * object.temperature #E = m*c*T
            elif isinstance(object, TwoSidedBlackbody): #TwoSidedBlackbodies have two sides with different temperatures.
                total_energy += object.mass_left * object.specific_heat_left * object.temperature_left #E = m*c*T for the left side.
                total_energy += object.mass_right * object.specific_heat_right * object.temperature_right #E = m*c*T for the right side.
        return total_energy 
        
    def main(self): #The heart of our simulation. This is what the computer is executing while our simulation is running.
        while self.running: #Infinite loop. We will do these things over and over on repeat until our self.running variable gets set to False.
            self.events() #Check for any new events we need to act on
            self.update() #Update all of the things that move/change
            self.draw() #Redraw the screen, since things may have moved/changed.
            #self.clock.tick(60) #60FPS. This just tells python to wait. The simulation is only allowed to execute this line 60 times per second.
            
if __name__ == "__main__": #This code only runs if we are running this file directly, and not importing it as a module in another file.
    pygame.init()
    simulation = Simulation() #First, we make a Simulation object, calling its constructor. We save it to a variable so can access it later.
    simulation.create() #We point to our simulation object and tell it to execute its create method. This builds the initial world and sets things up.
    simulation.main() #We point to our simulation object and tell it to execute its main method. This method contains an infinite loop and will continue to run while they are playing.
    pygame.quit() #We can only make it to here if the infinite loop from main ended, which means we want to stop the simulation, so we quit.