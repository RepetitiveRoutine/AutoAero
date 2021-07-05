# AutoAero
Aerodynamic automation script to join Ansys Fluent with Ensight for Curtin Motorsport Team


###########################
        CHANGELOG 
###########################


03/03/21

	NOTE:
	Implemented the new Ensight Scripts (v3.3), and SS-WRAP journal.
	There is still no Yaw functionality.


05/07/21    

	NOTE:
	Removed the ability for people to run singular yaw/ss sims.
	Reasoning was because there isnt much point in asking. The sim
	now assumes based off how many scdocs are present in the directory.

	Autoaero now can delete everything inside the simulations folder via
	the menu. This is more of a convenience for development. 

	The script will now exit whenever it finds that a directory for a sim
	already exists. That is to say, if you run SS21-1000 and then run it again
	without deleting the folder then AutoAero will exit to avoid issues.


