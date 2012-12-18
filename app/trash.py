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