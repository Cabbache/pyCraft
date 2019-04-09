# Art bot
This minecraft bot can draw .jpg images with blocks on plot surfaces.
The pyCraft library was modified and some packets were added to make this possible.

### Dependencies
Apart from the dependencies listed for pyCraft, this requires **PIL** for **Image**
https://pythonware.com/products/pil/

### Usage
It is not very user friendly and it is specifically made to work with the creative server on **play.extremecraft.net**,
so it will require some modifiactions if it will be used on other servers. pic.jpg, art.py and minecraft (folder) must be in the
same folder for this to work. Make sure you change the 'USR' and 'PWD' variables in the code to that of a valid account
on the server. Run art.py and you should have a console. Enter 'draw' so that the bot starts drawing, parameters are separated with semi colon. Check the code to see what commands it takes. 

**Examples:**
* \>\> ch:hello players
* \>\> draw:intel
* \>\> draw:cont
* \>\> ch:/p auto
* \>\> verb

There is a problem which causes the bot to get kicked often during printing. For linux users a solution to this is executing art.py like this: **while sleep 9;do echo "draw:cont" | timeout 350s python art.py;done** to stop it you must then do **kill -9 [pid]**. to find the pid do **ps aux**
