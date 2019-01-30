# Art bot
This minecraft bot can draw .jpg images with blocks on plot surfaces.
The pyCraft library was modified and some packets were added to make this possible.

### Dependencies
Apart from the dependencies listed for pyCraft, this requires **scipy** and **numpy**

### Usage
It is not very user friendly and it is specifically made to work with the creative server on **play.extremecraft.net**,
so it will require some modifiactions if it will be used on other servers. pic.jpg, art.py and minecraft (folder) must be in the
same folder for this to work. Make sure you change the 'USR' and 'PWD' variables in the code to that of a valid account
on the server. Run art.py and you should have a console. Enter 'draw' so that the bot starts drawing, parameters are separated with semi colon. Check the code to see what commands it takes. 
**Examples:**
* \<foo> ch:hello players
* >> draw:intel
* >> draw:cont
* >> ch:/p auto
* >> verb
