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
    
    pieces = match.match_piece.order("time_tag").filter("funfact =", False).order("time_tag")

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


class Testing(webapp.RequestHandler):
    def get(self):
        team = models.Team.team_from_name("Brazil")
        self.response.out.write(team.national)
      

class InitPieces(webapp.RequestHandler):
    def get(self, match_key):
        match = db.get(match_key)
 
        if match.name == "Brazil - Norway":
            comments = [
                ["Starting Lineups", "50"],
                ["Match start", "119"],
                ["We at ESPN wish to thank Budweisser, The US Army, FedEx, Nike, National Car Rental, British Airways and Canon for allowing us to bring you tonights game commercial free!", "128"],
                ["Corner for Norway", "137"],
                ["Shot by Rekdal", "158"],
                ["Chance for Ronaldo, but Bebeto is offisde", "342"],
                ["Huge chance for Brazil, great pass by Ronaldo. Bebeto's just a foot short of scoring", "5024"],
                ["Goal Brazil! Header by Bebeto", "5114"],
                ["Sub: xxx (out) <-> J. Flo (in)", "5189"],
                ["Goal Norway! Tore Andre Flo", "5417"],
                ["This is Tore Andre Flo's 13th international goal)", "5441"],
                ["Chance for Norway, J. Flo's heades towards his brother T.A. Flo, but the latter fails to convert", "5502"],
                ["Chance for Norway. The Flo brothers are causing trouble for the Brazilian defence once again", "5542"],
                ["Penalty for Norway. T.A. Flo is pulled down by Baiano", "5586"],
                ["Rekdal to take the penalty", "5729"],
                ["Goal Norway! Rekdal scores!", "5770"],
                ["Norway are now through to the next round", "5786"],
                ["E. Olsen, very anxious to see the game finished", "5956"],
                ["Free kick for Brazil. Carlos to shoot?", "6065"],
                ["Shot saved by Grodas", "6085"],
                ["Game over. Norway are through", "6100"],
                ["corner for Norway", "1334"],
                ["Bjornebye", "1356"],
                ["Aweful corner by Bjornebye", "1370"],
                ["Free kick for Norway", "2433"],
                ["Ronaldo. The slim version!", "344"],
            ]
        
            for c in comments:
                piece = models.Piece()
                piece.content = c[0]
                piece.time_tag = int(c[1])
                piece.match = match
                piece.put()

            self.redirect("../../match?match_key=%s" % match_key)

        else:
            self.response.out.write("There are no pre-defined comments for this match")


class InitTeams(webapp.RequestHandler):
  def get(self):

    teams = ["Scotland", "Norway", "Brazil", "Morocco"]

    for t in teams:
        team = models.Team()
        team.name = t
        team.national = True
        team.put()

    self.response.out.write("Added the following teams: " + str([t for t in teams]),)

class InitStadiums(webapp.RequestHandler):
  def get(self):

    stadiums = [
        ["Stade Velodrome", "42000", "The Stade Velodrome is a football stadium in Marseille, France. It is home to the Olympique de Marseille football club of Ligue 1"],
        ["Stade de France", "80000", "The Stade de France is the national stadium of France, situated just north of Paris in the commune of Saint-Denis. It has an all-seater capacity of 81,338, making it the eighth largest stadium in Europe, and is used by both the France national football team and French rugby union team for international competition. On 12 July 1998, France defeated Brazil in the FIFA World Cup Final contested at the stadium."],
        ["Stade de la Mosson", "32000", "Stade de la Mosson is a football stadium in Montpellier, France. It is the home of Montpellier HSC (Ligue 1) and has a capacity of 32,900."], 
        ["Stade de la Beaujoire", "42000", "Stade de la Beaujoire is the home of the FC Nantes football club."],
        ["Stade Geoffroy-Guichard", "27000", "Stade Geoffroy-Guichard is used primarily for football matches, and tournaments such as the 1984 European Football Championship, the Football World Cup 1998 and the Confederations Cup 2003."],
        ["Stade Chaban-Delmas", "35000", "Stade Chaban-Delmas is a sporting stadium located in the city of Bordeaux, France. It is the home ground of FC Girondins de Bordeaux."]
    ]

    for s in stadiums:
        stadium = models.Stadium()
        stadium.name = s[0]
        stadium.capacity = int(s[1])
        stadium.information = s[2]
        stadium.put()

    self.response.out.write("Added the following stadiums: " + str([s[0] for s in stadiums]),)

class InitMatches(webapp.RequestHandler):
  def get(self):

    matches = [
        ["Brazil - Scotland", "http://bilder.vgb.no/1224/4col/img_44876e70eaf7f.jpg", "3QgGAnWL-64", "55689", "Stade de France", "1998", "06", "10"],
        ["Morocco - Norway", "http://bilder.vgb.no/1224/4col/img_44876e70eaf7f.jpg", "HiOB66VXSGE", "45333", "Stade de la Mosson", "1998", "06", "10"],
        ["Scotland - Norway", "http://bilder.vgb.no/1224/4col/img_44876e70eaf7f.jpg", "wBIKzLJZiFY", "23422", "Stade Chaban-Delmas", "1998", "06", "16"],
        ["Brazil - Morocco", "http://bilder.vgb.no/1224/4col/img_44876e70eaf7f.jpg", "HiOB66VXSGE", "50000", "Stade de la Beaujoire", "1998", "06", "16"],
        ["Brazil - Norway", "http://bilder.vgb.no/1224/4col/img_44876e70eaf7f.jpg", "m_nU1h8d0v0", "50000", "Stade Velodrome", "1998", "06", "23"],
        ["Scotland - Morocco", "http://bilder.vgb.no/1224/4col/img_44876e70eaf7f.jpg", "NPBBo2Z2QmY", "50000", "Stade Geoffroy-Guichard", "1998", "06", "23"],
    ]

    for m in matches:
        home, away = m[0].split(" - ")
        match = models.Match()
        match.name = m[0]
        match.thumnail = m[1]
        match.video_url = m[2]
        match.attendance = int(m[3])
        match.stadium = models.Stadium.stadium_from_name(m[4])
        match.date_played = datetime.date(int(m[5]), int(m[6]), int(m[7]))
        match.home_team = models.Team.team_from_name(home)
        match.away_team = models.Team.team_from_name(away)
        match.put()

    self.response.out.write("Added the following matches: " + str([m[0] for m in matches]),)



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



