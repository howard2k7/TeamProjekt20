# Teamprojekt20
Teamprojekt WS20_21 Team Rot


## TODO List


### GUI
- [ ] Create a dropdown menu for protocol (TCP / UDP)
- [x] Check the IP address textfield for sane input ([See help](https://stackoverflow.com/questions/3462784/check-if-a-string-matches-an-ip-address-pattern-in-python/48231784))
- [ ] Create a textfield for port and check for sane input
- [ ] Implement functions for the dropdown menus ("Höhe" and "Geschwindigkeit")
- [X] MessagePack implementation
- [X] connection button without lambda function ( NOT POSSIBLE*)
- [X] Show info about connected Gamepad
- [ ] Make shiny and pretty GUI (pink)
- [X] Show info about connected host IP address

*This does not work. You have to use functools with partial
        or lambda as if nothing is used, the function gets executed when
        the button is created. Another way would be to write wrapper functions
        around it but why should we if we can just use a simple lambda!?


### Gamepad
- [ ] Change angle conversion to radiant, seperate calculation for GUI
- [X] checking for is zero (interval/scope not absolute 0.0) (UNNÖTIG*)
- [ ] Set keymapping for GUI menu ("Höhe" and "Geschwindigkeit")

*Durch das Runden auf 1 Nachkommastelle wird sowieso alles bis 0.09 rausgefiltert 
und als 0.0 zurückgegeben. Deshalb ist es sinnvoll das so zu lassen und nicht
wie im Gespräch besprochen auf unsinnige Eventualitäten hin zu testen. So 
können wir die Empfindlichkeit selber einstellen (Hätte man sich vorher mit dem
Code anständig beschäftigt, hätte man das übrigens auch dem Herrn Schneider und Herrn
Engel sagen können. Wie auch der Fall oben mit der Lambda Funktion...) 

### COM
- [X] rename control function ("Host.py" line 77)
- [X] Show IP of connected host IP address (SYN/ACK)

### Communication with Robot group
- [ ] how to give them data (i.e. as instance of our host class)


### Documentation of the code
 - General documenting with more comments.
