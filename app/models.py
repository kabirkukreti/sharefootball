from google.appengine.ext import db

class Contributor(db.Model):
	user = db.UserProperty() # the userId for external users
	name = db.StringProperty() # user name
	country = db.StringProperty() #user country
	date_created = db.DateTimeProperty(auto_now_add=True) #date the userid was created
	date_edited = db.DateTimeProperty(auto_now=True) #date last edited
	email = db.StringProperty() #user email
	# face = db.StringProperty() #maybe for future use 
	# temp_store = db.StringProperty() #maybe for future use

class Team(db.Model):
	name = db.StringProperty() 
	icon_url = db.StringProperty() # flag / logo for the national or club team
	national = db.BooleanProperty() #boolean describing if the team is a nationl (1) of club (0).
	nickname = db.StringProperty() # team nickname given by its fans
	date_added = db.DateTimeProperty(auto_now_add=True)

	@classmethod
	def team_from_name(cls, name):
		return Team.all().filter("name =", name).fetch(10)[0]


class Stadium(db.Model):
	name = db.StringProperty()
	capacity = db.IntegerProperty()
	information = db.StringProperty()

	@classmethod
	def stadium_from_name(cls, name):
		return Stadium.all().filter("name =", name).fetch(10)[0]

class Match(db.Model):
	home_team = db.ReferenceProperty(Team, collection_name="home_team")
	away_team = db.ReferenceProperty(Team, collection_name="away_team")
	date_played = db.DateProperty()
	uploaded_by = db.ReferenceProperty(Contributor) #Uploaded by, foreign key to the contributor
	stadium = db.ReferenceProperty(Stadium)
	attendance = db.IntegerProperty()
	referee = db.StringProperty() # the match refereee
	state = db.IntegerProperty(default=0, choices=[0,1,2,3])
	  # 0-requested, 1-video, 2-some meta, 3-a lot of meta. These should automatically be updated by the site.
	name = db.StringProperty() # For making it easyer to referencing the match. The name is just the string combination of "home_team" - "away_team"
	video_url = db.StringProperty() # URL pointing to the match file
	start_point_1 = db.IntegerProperty() # point in video where the match starts
	start_point_2 = db.IntegerProperty() # point in video where the second half starts
	thumbnail = db.StringProperty() # URL pointing tumbnail 
	date_created = db.DateTimeProperty(auto_now_add=True) # The date for the match was added (autocomplete)
	date_edited = db.DateTimeProperty(auto_now=True) # Date the entity information was edited (not piece)

	
class Piece(db.Model):
	author = db.ReferenceProperty(Contributor) #referencing the contributor whom added the piece of information
	match = db.ReferenceProperty(Match, collection_name='match_piece') #referencing the match
	# state = db.IntegerProperty(default=1, choices=[0,1]) #Meaning if the piece is active or deleted. Only active pieces will be shown on the matchfeed.
	  # 0-deleted, 1-active
	rating = db.IntegerProperty() #number of likes or rating
	type = db.StringProperty(default = "General", choices=["Goal","Chance","Booking","Flair", "General"]) #All feeds are of a given type of feed,     optimaly what type is understood by the page itself (goal, chance, booking, tackle ...). 
	content = db.StringProperty() # the information itself.
	content_print = db.StringProperty()
	time_tag = db.IntegerProperty() # the inmatch time tag. This saves the matchtime for which the pieces of information belongs
	date_created = db.DateTimeProperty(auto_now_add=True) # Date the piece was added
	date_edited = db.DateTimeProperty(auto_now=True) # date last edited/ change of state.
	funfact = db.BooleanProperty(default = False)

	@property
	def time_tag_minutes(self): # same as time_tag, but just the minutes
		return ((self.time_tag - (self.time_tag % 60)) / 60)


class Player(db.Model):
	given_name = db.StringProperty() # not in use yet
	given_name_acr = db.StringProperty()
	family_name = db.StringProperty() # not in use yet
	name = db.StringProperty()
	# aliases = db.ListProperty(??) # to store alternate versions of the name
	nickname = db.StringProperty() #name the player is refered to by his fans
	date_born = db.DateProperty() # birth date of player
	position = db.StringProperty() #main og most usual position
	bio = db.StringProperty() #wikipedia scratch for information on the page
	height = db.StringProperty() # height of player in cm
	freebase_id = db.StringProperty()
	date_added = db.DateTimeProperty(auto_now_add=True)

class Appearance(db.Model):
	# This property links the player, team and match desiribing which player played for which team in which match, and on what postion.
	player = db.ReferenceProperty(Player)
	player_static = db.StringProperty()
	match = db.ReferenceProperty(Match)
	team = db.ReferenceProperty(Team)
	number = db.IntegerProperty()
	on_field = db.IntegerProperty(choices = [0,1,2])
	  # 0-unused sub, 1-sub, 2-starting line up
	position_played = db.StringProperty()

class Suggestions(db.Model):
	suggestor = db.ReferenceProperty(Contributor) #referencing the contributer whom added the suggestion.
	suggestion = db.StringProperty() # The suggestion itself.
	date_created = db.DateTimeProperty(auto_now_add=True) # Date the suggestion was added.

class Funfact(db.Model):
	author = db.ReferenceProperty(Contributor) #referencing the contributer whom added the piece of information
	state = db.IntegerProperty(default=1, choices=[0,1]) #Meaning if the piece is active or deleted. Only active pieces will be shown on the matchfeed.
	  # 0-deleted, 1-active
	rating = db.IntegerProperty() #number of likes or rating
	category = db.StringProperty(default = "interesting event", choices=["Goal","Chance","Booking","Flair"]) #All feeds are of a given type of feed, optimaly what type is understood by the page itself (goal, chance, booking, tackle ...). 
	content = db.StringProperty() # the information itself.
	date_created = db.DateTimeProperty(auto_now_add=True) # Date the piece was added
	date_edited = db.DateTimeProperty(auto_now=True) # date last edited/ change of state.
	
class Competition(db.Model):
	year = db.IntegerProperty()


class Development(db.Model):
	init_matches = db.BooleanProperty(default = False)
	init_comments = db.BooleanProperty(default = False)


