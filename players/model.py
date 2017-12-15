from models import Player


class Model(object):
    def __init__(self):
        super(Model, self).__init__()
        self.temporary_object = None
        self.bulk_players_to_update = []
        self.bulk_players_to_create = []

    @staticmethod
    def new_player(code, name, fullname):
        """new_player(code, name, fullname) -> player object"""
        player = Player.objects.create(code=int(code),
                                       name=name.upper(),
                                       fullname=fullname.upper())
        return player

    @staticmethod
    def get_player_by_name(name):
        """get_player_by_name(name) -> player object"""
        return Player.objects.filter(name=name.upper()).all()

    @staticmethod
    def get_player_by_code(code):
        """get_player_by_code(code) -> player object"""
        return Player.objects.filter(code=int(code)).first()

    @staticmethod
    def get_players():
        """get_players() -> iterable"""
        return Player.objects.order_by('code').all()

    def set_temporary_object(self, obj):
        print "[DEBUG] %s in-memory object setting..." % type(obj)
        self.temporary_object = obj

    def get_temporary_object(self):
        print "[DEBUG] %s in-memory object retrieving..." % \
              type(self.temporary_object)
        return self.temporary_object

    def import_all_players(self):
        Player.objects.bulk_create(self.bulk_players_to_create)

    def clear_bulk_players(self):
        self.bulk_players_to_create = []

    @staticmethod
    def get_players_count():
        return Player.objects.count()

    @staticmethod
    def delete_all_players():
        Player.objects.all().delete()

    def delete_player(self, code):
        player = self.get_player_by_code(int(code))
        if player:
            player.delete()

    def add_new_player_to_bulk(self, code, name, fullname):
        name = u'%s' % name.upper()
        player = Player(code=int(code), name=name, fullname=fullname)
        self.bulk_players_to_create.append(player)

    @staticmethod
    def get_players_ordered_by_filter(filter_name):
        return Player.objects.order_by(filter_name).all()

    @staticmethod
    def get_players_by_name(surname):
        return Player.objects.filter(name=surname.upper()).all()

    def update_player(self, code, name, fullname):
        player = self.get_player_by_code(int(code))
        if not player:
            player = self.get_temporary_object()
        player.code = code
        player.name = name.upper()
        player.fullname = fullname.upper()
        player.save()
        print "INFO: Player %s updated!" % name
        return player

    @staticmethod
    def check_full_duplicated_names():
        for p in Player.objects.all():
            if Player.objects.filter(
                    name=p.name).count() > 1:
                print "WARNING: full duplicated name -> %s [%s]" \
                      % (p.name, p.code)

    @staticmethod
    def check_partial_duplicated_names():
        duplicated = []
        for p in Player.objects.all():
            p_name = p.name
            if '.' in p_name:
                p_name = ' '.join(p_name.split(' ')[:-1])
            query = Player.objects.filter(name__startswith=p_name)
            count = query.count()
            if count > 1 and p not in duplicated:
                duplicated.append(p)

        for p in duplicated:
            print "WARNING: partial duplicated name -> %s [%s]" \
                  % (p.name, p.code)

#                if p not in duplicated:
#                    print p.name
#                    duplicated.append(p)

#        for pl in duplicated:
#            if Player.objects.filter(
#                    name__startswith=pl.name.split(' ')[0]).count() > 1:
#                print "WARNING: partial duplicated name -> %s [%s]" \
#                          % (pl.name, pl.code)
