import os
import json
import re
import urllib2
from bs4 import BeautifulSoup

import wx

from model import Model
from gazzetta.spiders.gazzetta_spider import GazzettaSpider
from gazzetta.spiders.names_spider import NamesSpider
from players.views.core import Core

# import to avoid two reactor: Reactor is not restartable
from scrapy.crawler import CrawlerProcess


class Controller(object):
    def __init__(self):
        app = wx.App()
        self.model = Model()
        self.view = Core(parent=None, controller=self, title='Players')
        self.names_path = 'names.csv'
        self.gazzetta_path = 'gazzetta.json'
        self.names = []
        self.d_names = {}
        app.MainLoop()

    @staticmethod
    def _run_names_spider():
        process = CrawlerProcess({'FEED_FORMAT': 'csv',
                                  'FEED_URI': 'names.csv'})
        process.crawl(NamesSpider)
        process.start()

    @staticmethod
    def prettify(string):
        values = string.strip().split('_')
        values = [v for v in reversed(values)]
        # special = values[1].upper()
        if len(values) > 3:
            part_1 = values[1]
            part_2 = values[2]
            values[1] = part_2
            values[2] = part_1
        code = values[0]
        name = ' '.join(values[1:]).upper()
        return code, name

    def import_players(self):
        if self.names_path in os.listdir(os.getcwd()):
            print "INFO: old players file found, deleting..."
            os.remove(self.names_path)
        print "INFO: 'names' spider run to catch player names"
        self._run_names_spider()  # run spider to extract all names
        self.names_path = 'names.csv'
        print "INFO: %s created!" % self.names_path
        print "INFO: parsing names.csv..."
        with open(self.names_path) as f:
            # create a list with all names from names.csv except the first line
            # that it's not a player name, see names.csv.
            self.names = [line.strip() for line in f.readlines()][1:]
        # translate every names
        self.view.set_range(len(self.names))

        print "INFO: generating player names database..."
        count = 1
        for string in self.names:
            code, name = self.prettify(string)
            self.save_initial_name(code, name)  # salvo su db
            self.view.set_progress(count)
            self.view.Update()
            count += 1
        self.commit_all_players()

        print "INFO: correcting duplicated player names..."
        for player in self.get_players():
            self.correct_duplicates(player.name.upper())
        print "INFO: Success!"
        self.view.show_message("Success!")

    def save_initial_name(self, code, name):
        values = name.split(' ')
        surname = values[0].upper()
        if len(values) > 2:
            surname = ' '.join(values[:2])
        self.import_player_bulk(code, surname, name)

    def correct_duplicates(self, surname):
        duplicates = self.model.get_players_by_name(surname)
        if len(duplicates) > 1:
            duplicated_names = []
            for player in duplicates:
                print "WARNING: found duplicated name for player %s" \
                      % player.name
                new_name = '%s %s.' % (player.name,
                                       player.fullname.split(' ')[1][0])
                print "         ...corrected in %s" % new_name
                duplicated_names.append(new_name)
                player.name = new_name
                player.save()

            for new_surname in duplicated_names:
                if duplicated_names.count(new_surname) > 1:
                    new_duplicates = self.model.get_players_by_name(new_surname)
                    for player in new_duplicates:
                        print "WARNING: found duplicated name for player %s" \
                              % new_surname
                        new_name = '%s %s.' % (
                            player.fullname.split(' ')[0],
                            player.fullname.split(' ')[1][:2])
                        print "         ...corrected in %s" % new_name
                        player.name = new_name
                        player.save()

    def are_evaluations_ready(self, day):
        players = self.get_players()
        gazza_url = "http://www.gazzetta.it/calcio/fantanews/" \
                    "statistiche/serie-a-2017-18/"
        index = 1
        while True:
            player = players[len(players) - index]
            print "INFO: testing evaluations for %s..." % player.fullname
            try:
                name, surname = player.fullname.lower().split(' ')
                url = "%s%s_%s_%s" % (gazza_url, name, surname, player.code)
                page = urllib2.urlopen(url)
                soup = BeautifulSoup(page, 'html.parser')
                data = soup.find('li', attrs={'class': 'day-%s' % day})
                return True if data else False
            except ValueError:
                index += 1

    def get_code(self, string):
        return [k for k, v in self.d_names.iteritems()
                if v[0] == string.strip()][0]

    def get_player_by_name(self, name):
        return self.model.get_player_by_name(name)

    def get_player_by_code(self, code):
        return self.model.get_player_by_code(code)

    def get_players(self):
        return self.model.get_players()

    def save_player(self, code, name, fullname):
        player_object = self.get_player_by_code(code)
        if player_object:
            self.view.show_message("WARNING: Player already exists")
        else:
            new_player = self.model.new_player(code, name, fullname)
            self.view.show_message("INFO: New Player %s saved"
                                   % new_player.name)

    def set_temporary_object(self, obj):
        self.model.set_temporary_object(obj)

    def get_temporary_object(self):
        return self.model.get_temporary_object()

    def delete_player(self, code):
        return self.model.delete_player(code)

    def delete_all_players(self):
        return self.model.delete_all_players()

    def commit_all_players(self):
        self.model.import_all_players()

    def import_player_bulk(self, code, name, fullname):
        self.model.add_new_player_to_bulk(code, name, fullname)

    def get_sorted_players(self, id_c):
        columns = {0: 'code', 1: 'name', 2: 'fullname'}
        return self.model.get_players_ordered_by_filter(columns.get(id_c))

    def update_player(self, code, name, fullname):
        return self.model.update_player(code, name, fullname)

    @staticmethod
    def _run_evaluations_spider(day):
        process = CrawlerProcess({'FEED_FORMAT': 'json',
                                  'FEED_URI': 'gazzetta.json'})
        process.crawl(GazzettaSpider, day=day)
        process.start()

    def extract_evaluations(self, day):
        if self.gazzetta_path in os.listdir(os.getcwd()):
            print "INFO: old gazzetta json file found, deleting..."
            os.remove(self.gazzetta_path)
        self.view.set_status_text("INFO: running 'gazzetta' spider...")
        # run spider to extract all evaluations
        self.view.set_range(2)
        self.view.set_progress(1)
        self._run_evaluations_spider(day)
        self.write_mcc_file(day)
        self.view.set_progress(2)

    @staticmethod
    def generate_dict_from_json_file(path):
        with open(path) as f:
            data = json.loads(f.read())
        return {int(d.get('code')): d for d in data}

    @staticmethod
    def vote_correction(code, fv, gol):
        old_fv = fv
        fv = float(fv)
        if int(code) < 800 and int(gol) > 0:
            # add 0.5 for each goal scored if TQ is a midfielder
            fv += (0.5 * int(gol))
        elif int(code) > 800 and int(gol) > 0:
            # substract 0.5 for each goal scored if TQ is a forward
            fv -= (0.5 * int(gol))
        print "[INFO] TQ detected for code %s: %s -> %s" % (code, old_fv, fv)
        return fv

    @staticmethod
    def team_prettify(link):
        pattern = ".+rosa_(\w{3}).+shtml"
        prettified_team = re.compile(pattern).match(link).group(1)
        return prettified_team.upper()

    def write_mcc_file(self, day):
        print "INFO: %s created!" % self.gazzetta_path
        output_file_tq = "MCC%s.txt" % day
        output_file_no_tq = "MCCNOTQ%s.txt" % day
        for f in (output_file_no_tq, output_file_tq):
            if f in os.listdir(os.getcwd()):
                print "WARNING: old %s file found, deleting..." % f
                os.remove(f)

        print "INFO: Creating day %s files..."
        print "INFO: Generating dictionary from json file"
        try:
            json_dict = self.generate_dict_from_json_file(self.gazzetta_path)
        except IOError:
            print "ERROR: file %s not found!" % self.gazzetta_path
        else:
            f_tq = open(output_file_tq, "w")
            f__no_tq = open(output_file_no_tq, "w")
            print "[INFO] Generating MCC string..."
            self.view.set_range(len(self.get_players()))
            self.view.set_progress(0)
            count = 1
            for code in sorted(json_dict.keys()):
                self.view.set_progress(count)
                print "INFO: elaborating code %s..." % code
                data = json_dict.get(code)
                player = self.get_player_by_code(code)
                if not player:
                    print "INFO: inserting new player with code %s..." % code
                    code, name = self.prettify(data.get('link').split('/')[-1])
                    new_name = name.split(' ')[0]
                    self.save_player(code=int(code), name=new_name.upper(),
                                     fullname=data.get('name').upper())
                    player = self.get_player_by_code(code)
                name = player.name
                team = self.team_prettify(data.get('team'))
                v = data.get('v')
                q = data.get('q')
                gol = data.get('gol')
                ruolo = data.get('ruolo')
                fv = data.get('fv')
                fv_no_tq = data.get('fv')
                if ruolo == 'T' and float(v) > 0:
                    fv_no_tq = self.vote_correction(code, fv, gol)
                string = '{}|{}|{}|{}|{}|{}\n'.format(code, name, team,
                                                      fv, v, q)
                string_no_tq = '{}|{}|{}|{}|{}|{}\n'.format(code, name, team,
                                                            fv_no_tq, v, q)
                f_tq.write(string)
                f__no_tq.write(string_no_tq)
                count += 1
                   
            f_tq.close()
            f__no_tq.close()
            print "INFO: Success!"
            self.view.show_message("INFO: Success!")
