import os
import datetime
import logging
import time
import string

from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
import models

# import freebase
import json
from django.utils import simplejson
import datetime
import random


class Sandbox(webapp.RequestHandler):
    def get(self):
        template_values = {
            'none', 'none',
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/sandbox.html')
        self.response.out.write(template.render(path, template_values))

class Search(webapp.RequestHandler):
  def get(self):
    user_details = login_check(self)
    query = self.request.get('q')
    teams = models.Team.all().fetch(1000)
    team_names = [t.name for t in teams]
    
    template_values = {
      'query': query,
      'user': user_details[0],
      'url': user_details[1],
      'url_linktext': user_details[2],
      'contributor': user_details[3],
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/search.html')
    self.response.out.write(template.render(path, template_values))


class IndexHandler(webapp.RequestHandler):
  def get(self):
    user_details = login_check(self)

    matches = models.Match.all().fetch(1000)
    
    contributor = ""

    template_values = {
      'matches': matches,
      'user': user_details[0],
      'url': user_details[1],
      'url_linktext': user_details[2],
      'contributor': user_details[3],
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    self.response.out.write(template.render(path, template_values))

#class APIPieces(webapp.RequestHandler):
#  def get(self):
#    q = models.Piece.all()
#    q.order("-date_created")
#    pieces = q.fetch(10)

    
class Team(webapp.RequestHandler):
  def post(self):
    team = models.Team()
    team.name = self.request.get('name')
    team.put()

    self.redirect('../admin')


class Match(webapp.RequestHandler):
  def get(self):
    user_details = login_check(self)
    match = models.Match.get(self.request.get('match_key'))
    home_team = match.home_team.key()
    away_team = match.away_team.key()
    
    pieces = match.match_piece.order("time_tag").filter("funfact =", False)

    # dette kan trolig gjoeres paa en langt lurere maate:
    try:
    	q = models.Appearance.all()
    	q.filter("match =", match)
    	q.order("number")
    	appearances = q.fetch(50)

    	appearances_home = [a for a in appearances if a.team.key()==home_team]
    	appearances_away = [a for a in appearances if a.team.key()==away_team]
    except:
	    appearances = []
 
    q2 = models.Piece.all()
    q2.filter("funfact =", True)
    funfacts = q2.fetch(100)       # liste med piece-objekter
    funfacts = [f.content for f in funfacts]      # liste med funfact-strings
						
    template_values = {
		'post_url': "/piece",
                'appearances': appearances,
                'appearances_home': appearances_home,
                'appearances_away': appearances_away,
                'pieces': pieces,
		'match': match,
		'funfacts': funfacts,
		'user': user_details[0],
		'url': user_details[1],
		'url_linktext': user_details[2],
		'contributor': user_details[3],
				}
    path = os.path.join(os.path.dirname(__file__), 'templates/match.html')
    self.response.out.write(template.render(path, template_values))
  def post(self):
    match = models.Match()
    match.home_team = team_from_name(self.request.get('home_team'))
    match.away_team = team_from_name(self.request.get('away_team'))
    match.name = match.home_team.name + " - " + match.away_team.name
    match.put()
    self.redirect('/add')

class UserDetails(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    template_values = {
				'user': user,
				}
    path = os.path.join(os.path.dirname(__file__), 'templates/userdetails.html')
    self.response.out.write(template.render(path, template_values))
  def post(self):
		user = users.get_current_user()
		contributor = models.Contributor()
		contributor.name = self.request.get('name')
		contributor.country = self.request.get('country')
		contributor.user = user

		contributor.put()
		self.redirect('../')


class Piece(webapp.RequestHandler):
  def post(self):
    piece = models.Piece()
    user = users.get_current_user()
    if user:
      piece.author = models.Contributor.all().filter("user =", user).fetch(1)[0]
    piece.match = models.Match.get(self.request.get('match_key'))
    piece.content = self.request.get('raw') # TODO: FIKS
    piece.time_tag = int(self.request.get('time_tag'))
    piece.time_tag_minutes = ((piece.time_tag - (piece.time_tag % 60)) / 60)

    piece.put()
    # self.redirect('../match?match_key=%s' % self.request.get('match_key'))


class Appearance(webapp.RequestHandler):
  def post(self):
    # player = player_from_name(self.request.get('name')
    raw = self.request.get('raw')
    temp = raw.split(":")

    appearance = models.Appearance()
    appearance.player_static = temp[1].strip()
    appearance.match = models.Match.get(self.request.get('match_key'))
    appearance.team = models.Team.get(self.request.get('team_key'))
    appearance.number = int(temp[0].strip())
    appearance.put()

    self.redirect('../match?match_key=%s' % self.request.get('match_key'))


class Classify(webapp.RequestHandler):
  def get(self):
    user_details = login_check(self)
    pieces = models.Piece.all().fetch(500)
    length = len(pieces)
    r = random.randint(0, length)
    piece = pieces[r]
     
    template_values = {
      'length': length,
      'r': r,
      'piece': piece,
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/classify.html')
    self.response.out.write(template.render(path, template_values))

class Admin(webapp.RequestHandler):
  def get(self):
    user_details = login_check(self)
    matches = models.Match.all().order("date_created").fetch(100)
    teams = models.Team.all().fetch(100)
    contributors = models.Contributor.all().fetch(100)
    players = models.Player.all().fetch(500)
     
    template_values = {
      'matches': matches,
      'teams': teams,
      'contributors': contributors,
      'players': players,
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/admin.html')
    self.response.out.write(template.render(path, template_values))

class AdminMatch(webapp.RequestHandler):
  def get(self):
    user_details = login_check(self)
    match = models.Match.get(self.request.get('key'))
     
    template_values = {
      'match': match,
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/admin_match.html')
    self.response.out.write(template.render(path, template_values))


class Delete(webapp.RequestHandler):
  """Generic delete"""
  def post(self):
    entity = db.get(self.request.get("key"))
    db.delete(entity)


class Clear(webapp.RequestHandler):
  def get(self):
    try:
      q = models.Player.all()
      players = q.fetch(1000)
      db.delete(players)

      q = models.Appearance.all()
      appearances = q.fetch(1000)
      db.delete(appearances)

      q = models.Match.all()
      matches = q.fetch(100)
      db.delete(matches)

      q = models.Piece.all()
      pieces = q.fetch(1000)
      db.delete(pieces)

      q = models.Team.all()
      teams = q.fetch(1000)
      db.delete(teams)

      q = models.Stadium.all()
      stadiums = q.fetch(1000)
      db.delete(stadiums)

      self.response.out.write("Databasen slettet!")
      
    except:
      self.response.out.write("Noe gikk galt")
      

class InitComments(webapp.RequestHandler):
    def get(self):
        matches = models.Matches.all().fetch(100)
        matches.filter("name =", "Brazil - Norway")
        self.response.out.write(matches.key())

class Init(webapp.RequestHandler):
  def get(self):

    teams = models.Team()
    teams.name = "Scotland"
    teams.national = True
    teams.put()

    teamn = models.Team()
    teamn.name = "Norway"
    teamn.national = True
    teamn.put()

    teamb = models.Team()
    teamb.name = "Brazil"
    teamb.national = True
    teamb.put()

    teamm = models.Team()
    teamm.name = "Morocco"
    teamm.national = True
    teamm.put()
    
    stadion1 = models.Stadium()
    stadion1.name = "Stade Velodrome"
    stadion1.capacity = 42000
    stadion1.information = "The Stade Velodrome is a football stadium in Marseille, France. It is home to the Olympique de Marseille football club of Ligue 1"
    stadion1.put()

    stadion2 = models.Stadium()
    stadion2.name = "Stade de France"
    stadion2.capacity = 80000
    stadion2.information = "The Stade de France is the national stadium of France, situated just north of Paris in the commune of Saint-Denis. It has an all-seater capacity of 81,338, making it the eighth largest stadium in Europe, and is used by both the France national football team and French rugby union team for international competition. On 12 July 1998, France defeated Brazil in the FIFA World Cup Final contested at the stadium."
    stadion2.put()

    stadion3 = models.Stadium()
    stadion3.name = "Stade de la Mosson"
    stadion3.capacity = 32000
    stadion3.information = "Stade de la Mosson is a football stadium in Montpellier, France. It is the home of Montpellier HSC (Ligue 1) and has a capacity of 32,900."
    stadion3.put()

    stadion6 = models.Stadium()
    stadion6.name = "Stade de la Beaujoire"
    stadion6.capacity = 42000
    stadion6.information = "Stade de la Beaujoire is the home of the FC Nantes football club."
    stadion6.put()

    stadion4 = models.Stadium()
    stadion4.name = "Stade Geoffroy-Guichard"
    stadion4.capacity = 27000
    stadion4.information = "Stade Geoffroy-Guichard is used primarily for football matches, and tournaments such as the 1984 European Football Championship, the Football World Cup 1998 and the Confederations Cup 2003."
    stadion4.put()

    stadion5 = models.Stadium()
    stadion5.name = "Stade Chaban-Delmas"
    stadion5.capacity = 35000
    stadion5.information = "Stade Chaban-Delmas is a sporting stadium located in the city of Bordeaux, France. It is the home ground of FC Girondins de Bordeaux."
    stadion5.put()
    
    test1 = models.Match()
    test1.thumbnail="http://bilder.vgb.no/1224/4col/img_44876e70eaf7f.jpg"
    test1.video_url="3QgGAnWL-64"
    test1.name = "Brazil - Scotland"
    test1.year = 1998
    test1.attendance = 556893
    test1.stadium = stadion2
    test1.date_played = datetime.date(1998, 06, 10)
    test1.home_team = teamb
    test1.away_team = teams
    test1.put()

    test2 = models.Match()
    test2.thumbnail="http://bilder.vgb.no/1224/4col/img_44876e70eaf7f.jpg"
    test2.video_url="HiOB66VXSGE"
    test2.name = "Morocco - Norway"
    test2.year = 1998
    test2.attendance = 45333
    test2.date_played = datetime.date(1998, 06, 10)
    test2.stadium = stadion3
    test2.home_team = teamm
    test2.away_team = teamn
    test2.put()

    test3 = models.Match()
    test3.thumbnail="http://bilder.vgb.no/1224/4col/img_44876e70eaf7f.jpg"
    test3.video_url="wBIKzLJZiFY"
    test3.name = "Scotland - Norway"
    test3.year = 1998
    test3.attendance = 23422
    test3.date_played = datetime.date(1998, 06, 16)
    test3.stadium = stadion5
    test3.home_team = teams
    test3.away_team = teamn
    test3.put()

    test4 = models.Match()
    test4.thumbnail="http://bilder.vgb.no/1224/4col/img_44876e70eaf7f.jpg"
    test4.video_url="HiOB66VXSGE"
    test4.name = "Brazil - Morocco"
    test4.year = 1998
    test4.date_played = datetime.date(1998, 06, 16)
    test4.stadium = stadion6
    test4.home_team = teamb
    test4.away_team = teamm
    test4.put()

    test5 = models.Match()
    test5.thumbnail="http://bilder.vgb.no/1224/4col/img_44876e70eaf7f.jpg"
    test5.video_url="m_nU1h8d0v0"
    test5.name = "Brazil - Norway"
    test5.date_played = datetime.date(1998, 06, 23)
    test5.year = 1998
    test5.stadium = stadion1
    test5.home_team = teamb
    test5.away_team = teamn
    test5.put()

    test6 = models.Match()
    test6.thumbnail="http://bilder.vgb.no/1224/4col/img_44876e70eaf7f.jpg"
    test6.video_url="NPBBo2Z2QmY"
    test6.name = "Scotland - Morocco"
    test6.year = 1998
    test6.date_played = datetime.date(1998, 06, 23)
    test6.stadium = stadion4
    test6.home_team = teams
    test6.away_team = teamm
    test6.put()

#    piece1 = models.Piece()
#    piece1.match = test5
#    piece1.time_tag = 3610
#    piece1.content = "GOAL! Great goal by T. A. Flo. Norways fate remains undecided!"
#    piece1.put()

#    player1 = models.Player()
#    player1.nickname = "Rekdal"
#    player1.bio = "http://en.wikipedia.org/wiki/Kjetil_Rekdal"
#    #date_born = ????
#    player1.put()

#    appearance1 = models.Appearance()
#    appearance1.number = 10
#    appearance1.position_played = "Midfielder"
#    appearance1.player = player1
#    appearance1.match = test5
#    appearance1.put()


    self.response.out.write("Seks kamper lagt inn samt metadata til disse kampene er lagt inn. Slaa deg lose med tagging",)



class InitFunfacts(webapp.RequestHandler):
  def get(self):

    funfact1 = models.Piece()
    funfact1.content = "Carlos Caszely of Chile was the first player red carded in a World Cup tournament on June 14, 1974."
    funfact1.funfact = True
    funfact1.put()

    funfact2 = models.Piece()
    funfact2.content = "Jostein Flo lost 25 kilograms during the WorldCup 1998."
    funfact2.funfact = True
    funfact2.put()

    funfact3 = models.Piece()
    funfact3.content = "A Soccer player runs an average of 6 miles during a game."
    funfact3.funfact = True
    funfact3.put()

    funfact4 = models.Piece()
    funfact4.content = "The most World Cups have been won by Brazil-5."
    funfact4.funfact = True
    funfact4.put()

    funfact5 = models.Piece()
    funfact5.content = "Madagascan team Stade Olympique LEmryne scored 149 own goals against champions AS Adema in 2002. They repeatedly scored own goals in protest of a refereeing decision in their previous game."
    funfact5.funfact = True
    funfact5.put()

    funfact6 = models.Piece()
    funfact6.content = "India withdrew from the World Cup in 1950 because they werent allowed to play barefoot."
    funfact6.funfact = True
    funfact6.put()

    funfact7 = models.Piece()
    funfact7.content = "European Teams have reached the final of every World Cup except in 1930 and 1950."
    funfact7.funfact = True
    funfact7.put()

    funfact8 = models.Piece()
    funfact8.content = "Soccer (Football) is the most popular sport in the world. Over 1 billion fans watch World Cup Soccer on television."
    funfact8.funfact = True
    funfact8.put()

    funfact9 = models.Piece()
    funfact9.content = "20 red cards were shown during a 1993 game between Sportivo Ameliano and General Caballero in Paraguay. Brazils Pele is the only player to have won three World Cup winners medals (1958, 1962, and 1970)."
    funfact9.funfact = True
    funfact9.put()

    funfact10 = models.Piece()
    funfact10.content = "The fewest number of fans to watch a World Cup soccer game was the 300 in Uruguay in 1930."
    funfact10.funfact = True
    funfact10.put()

    funfact11 = models.Piece()
    funfact11.content = "Where is he now? Dan Eggen (born 13 January 1970 in Oslo) is a Norwegian football coach and former player. He is currently coaching Kolbotn in the Norwegian Premier League for women. He was capped 25 times for Norway, scoring two goals. He is also well known for his great hair"
    funfact11.funfact = True
    funfact11.put()


    self.response.out.write("Noen funfacts er lagt inn")
    
#class FreebaseUpdate(webapp.RequestHandler):
#  def get(self):
#    query = [{
#     "type":          "/soccer/football_player",
#     "id" : None,
#     "/people/person/nationality": "Norway",
#     "name":          None,
#     "/common/topic/alias" : [],
#     "/people/person/date_of_birth": None,
#     "/people/person/height_meters" : None,
#     "position_s":    [],
#     "limit":         10000,
#	  }]
    
#    try:
#      results = freebase.mqlread(query)
#    except:
#      self.response.out.write("Noe gikk galt med freebase query-et")

#    for r in results:
#      temp = models.Player()
#      temp.freebase_id = r.id
#      temp.name = r.name
#      temp.position = r.position_s[0]
#      temp.nickname = r["/common/topic/alias"][0]
#      temp.date_born = r["/people/person/date_of_birth"]
#      temp.height = r["/people/person/heigh_meters"]
#      temp.put()

#    self.response.out.write("Freebase-data lagt inn")





# FUNCTIONS

def login_check(self):
  user = users.get_current_user()
  url = users.create_login_url(self.request.uri)
  url_linktext = 'Login'
  contributor = -1
  if user:
    try:
      q = models.Contributor.all()
      q.filter("user =", user)
      contributor = q.fetch(1)[0]
      url_linktext = 'Logged in as %s, logout' % contributor.name
    except:
      self.redirect('../userdetails')
    url = users.create_logout_url(self.request.uri)
  return [user, url, url_linktext, contributor]

def team_from_name(name):
	q = models.Team.all()
	q.filter("name =", name)
	# skriv en try her med team = q.fetch(1)[1]
	return q.fetch(1)[0]


def player_from_name(name):
	"""Fetches a player object form a string"""
	q = models.Player.all()
	q.filter("name =", name)
	# skriv en try her med team = q.fetch(1)[1]
	return q.fetch(1)[0]

def keys_and_team_names():
   """returns a dict of keys and names for all teams"""
   q = models.Team.all()
   q.order("name") 
   teams = q.fetch(1000)
   keys = [t.key() for t in teams]
   names = [t.name for t in teams]
   dictionary = dict(zip(keys, names))
   return dictionary



