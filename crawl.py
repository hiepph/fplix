import urllib2
import time

# https://aicontest.framgia.vn/game/4843/replay.rpl
url = 'https://aicontest.framgia.vn/game'
cookie = 'session=.eJxNj8FqwkAURX-lvHUW7cRSDLgIxGAL8zQyVvKKBI2TTGecBibRtCP592rooou7PefcKxSVk62CqHNnGUDxeYToCg8HiIAna03J6cRF7Emv1W0G9WuIetOTJZPrMiQ779HzGQwBlM1R9ntXdI2RXyOlg-gDQpZOLT7J72nGF5NameaSZWwVz20tdAXBnw2G3Z3RuuofYMy4qZG9W2RkyG5-luJN8aR8zLXSfJta9KSWwnguakZb7pHlzxjPxqRzK914CSYvMPwCCtFMtA.C9Zjqw.OFVrQWaaXZesiur418fGDgIDCzM'
for i in range(2290, 13000):
  gameUrl = url + '/' + str(i) + '/replay.rpl'
  print 'Game ' + str(i)
  try:
    q = urllib2.Request(gameUrl)
    q.add_header('Cookie', cookie)
    conn = urllib2.urlopen(q)
  except urllib2.HTTPError as e:
    print e
  except urllib2.URLError as e:
    print e
  else:
    try:
        data = conn.read().split('|')
        file = open('game' + str(i) + '.txt', 'w')

        file.write('2\n')
        for line in data:
          splitData = line.split('$')
          move = None
          if len(splitData) > 1:
            splitData, move = splitData
          else:
            splitData = splitData[0]

          splitData = splitData.split(' ')
          state = splitData[0]

          for i in range(20):
            for j in range(30):
              file.write(state[30 * i + j])
            file.write('\n')

          # Position
          file.write(splitData[1] + ' ' + splitData[2] + '\n')
          file.write(splitData[3] + ' ' + splitData[4] + '\n')

          # Points
          file.write(splitData[5] + ' ' + splitData[6] + '\n')

          # Move
          if move is not None:
            file.write(move[0] + ' ' + move[1] + '\n')
    except IndexError:
        print 'Game %d failed index' % i
