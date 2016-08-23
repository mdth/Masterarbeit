import sys
from pymongo import MongoClient
from bson.code import Code
from math import log10
from pymongo.errors import ConnectionFailure

# Add try and catch for each operation and return the error !!


def connect():
    """ Connect to MongoDB """
    try:
        client = MongoClient()
        client = MongoClient('localhost', 27017)
        print("Connected successfully")
    except ConnectionFailure:
        sys.stderr.write("Could not connect to MongoDB: %s" % ConnectionFailure)
        sys.exit(1)
    db = client['network']
    return db


# insert returns the id of the insert document
def add_text(db, source):
    return db.texts.insert({"text_source": source})


def add_sentence(db, sent, id_text):
    return db.sentences.insert({"id_text": id_text, "content": sent})


def add_sop(db, subject, predicate, object, id_book, id_sent):
    db.IR.insert({"subject": subject, "object": object, "predicate": predicate, "id_book": id_book, "sent": id_sent})


def get_length_sop(db, id_text):
    return db.IR.count({"id_text": id_text})


def get_sub_list_occ(client):
    mapper = Code("""
            function(){
                var key = {"subject": this.subject};
    	        emit(key,1);}
    	                        """)
    reducer = Code("""
                    function (key, values) {
                    var sum = 0;
                     values.forEach(function(value)
                    {
                        sum += 1
                    });
            return sum;  }
                """)
    results = client.IR.map_reduce(mapper, reducer, "socc")
    socc = []
    for elm in results.find():
        socc.append(
            {"subject": elm['_id']['subject'],"count": elm['value']})
    return socc


def get_subject_occ(sub_occ_list, subject):
    dict = next(item for item in sub_occ_list if item["subject"] == subject)
    return dict['count']


def get_obj_list_occ(client):
    mapper = Code("""
            function(){
                var key = {"object":this.object };
    	        emit(key,1);}
    	                        """)
    reducer = Code("""
                    function (key, values) {
                    var sum = 0;
                     values.forEach(function(value)
                    {
                        sum += 1
                    });
            return sum;  }
                """)
    results = client.IR.map_reduce(mapper, reducer, "obj.occ")
    objocc = []
    for elm in results.find():
        objocc.append(
            {"object": elm['_id']['object'],
             "count": elm['value']})
    return objocc


def get_predicate_occ(client):
    mapper = Code("""
            function(){
                var key = {"predicate": this.predicate};
    	        emit(key,1);}
    	                        """)
    reducer = Code("""
                    function (key, values) {
                    var sum = 0;
                     values.forEach(function(value)
                    {
                        sum += 1
                    });
            return sum;  }
                """)
    results = client.IR.map_reduce(mapper, reducer, "pred.occ")
    pred = []
    for elm in results.find():
        pred.append(
            {"predicate": elm['_id']['predicate'],"count": elm['value']})
    return pred


def get_sub_obj_list_occ(client):
    mapper = Code("""
            function(){
                var key = {"object":this.object , "subject": this.subject};
    	        emit(key,1);}
    	                        """)
    reducer = Code("""
                    function (key, values) {
                    var sum = 0;
                     values.forEach(function(value)
                    {
                        sum += 1
                    });
            return sum;  }
                """)
    results = client.IR.map_reduce(mapper, reducer, "sub.obj")
    sop = []
    for elm in results.find():
        sop.append(
            {"subject": elm['_id']['subject'],"object": elm['_id']['object'],
             "count": elm['value']})
    return sop


# TODO this i need
def calculate_pmi(sub_occ, obj_occ, sub_obj_occ):
    """the number of items in the corpus is needed to calculate the pmi !!-> shallow parsing
    not all words are retrieved does it make sense ??"""
    # from the paper
    # pmi= freq(w,context)*jcorpus/freq(w)*freq(context)
    pmi = log10(sub_obj_occ / (sub_occ * obj_occ))
    return pmi


def sop_occ_list(client):
    # using map reduce !
    mapper = Code("""
        function(){
            var key = {"predicate": this.predicate, "object":this.object , "subject": this.subject};
	        emit(key,1);}
	                        """)
    reducer = Code("""
                function (key, values) {
                var sum = 0;
                 values.forEach(function(value)
                {
                    sum += 1
                });
        return sum;  }
            """)
    results = client.IR.map_reduce(mapper, reducer,"sop.occ")
    sop = []
    for elm in results.find():
        sop.append({"subject": elm['_id']['subject'], "predicate": elm['_id']['predicate'], "object": elm['_id']['object'],
                    "PMI": elm['value']})
    return sop

# 2 choices: update collection or create a new one -> UPDATE after first operation with the new values


def get_sub_obj_occ(sub_obj_occ, subject, object):
    dict = next(item for item in sub_obj_occ if item["subject"] == subject and item["object"] == object)
    return dict['count']


def get_object_occ(obj_occ, object):
    dict = next(item for item in obj_occ if item["object"] == object)
    return dict['count']


def create_sop_pmi_collection(database, sop_occ_list, sub_occ, obj_occ, sub_obj_occ):
    names = database.collection_names()
    if "sop" in names:
        database.sop.drop()
        for dict in sop_occ_list:
            dict["PMI"] = calculate_pmi(get_subject_occ(sub_occ, dict["subject"]),
                                        get_object_occ(obj_occ, dict["object"]),
                                        get_sub_obj_occ(sub_obj_occ, dict["subject"], dict["object"]))
    database.sop.insert(sop_occ_list)
    return database.sop.find()


def sub_vec(db):
    return db.sop.aggregate([{"$group": {"_id": "$subject", "predicates": {"$push": "$predicate"}, "objects": {"$push":
                                                                                                                   "$object"},
                                         "vector": {"$push": "$PMI"}}}])


def obj_vec(db):
    return db.sop.aggregate([{"$group": {"_id": "$object", "predicates": {"$push": "$predicate"},
                                         "subjects": {"$push": "$subject"}, "vector": {"$push": "$PMI"}}}])


def pre_vec(db):
    return db.sop.aggregate([{"$group": {"_id": "$predicate", "subjects": {"$push": "$subject"}, "objects": {"$push":
                                                                                                                 "$object"},
                                         "vector": {"$push": "$PMI"}}}])


def get_op_list(db):
    void = Code("""
            function(){
               }
                         """)
    return db.IR.group(
        key={"object": 'true', "predicate": 'true'}, condition={}, initial={},
        reduce=void)


def get_sp_list(db):
    void = Code("""
            function(){
               }
                         """)
    return db.IR.group(
        key={"subject": 'true', "predicate": 'true'}, condition={}, initial={},
        reduce=void)


def create_subjects_collection(db):
    coll = create_sop_pmi_collection(db, sop_occ_list(db), get_sub_list_occ(db), get_obj_list_occ(db),
                                     get_sub_obj_list_occ(db))
    # sparce = [0]*100
    subjects = db.sop.aggregate([{"$group": {"_id": "$subject", "predicates": {"$push": "$predicate"},
                                             "objects": {"$push": "$object"}, "vector": {"$push": "$PMI"}}}])
    final = []
    for i in subjects:
        sub_list = []
        sub = i['_id']
        for pred, obj, pmi in zip(i['predicates'], i['objects'], i['vector']):
            elm = {"predicate": pred, "object": obj, "weight": pmi}
            sub_list.append(elm)
        final.append({"sub_list": sub_list, "subject": sub})

    subjects = final
    # pred_obj_list = db.sop.aggregate([{"$group":{"_id":{"object":"$object","predicate":
    # "$predicate"},"predicates":{ "$push": "$predicate"},"objects":{ "$push": "$object"},"vector":{"$push": "$PMI"}}}])

    op = get_op_list(db)

    sub_matrix = []
    for subject in subjects:
        vector = [0] * len(op)
        sub = subject['subject']
        # for predicate , object in subject['predicates'] , subject['objects']:
        i = 0
        for col in op:
            for sp in subject['sub_list']:
                if col['predicate'] == sp['predicate'] and col['object'] == sp['object']:
                    vector[i] = sp['weight']

            i += 1
        # db.subjects.insert({"subject": sub, "vector": vector})
        sub_matrix.append({"subject": sub, "vector": vector})
    db.subjects.insert(sub_matrix)

########################################################################################################################
################# funtions for NOUN/adj pairs ####################################################################
##############################################################


def store_noun_adj(db, noun, adj):
    db.noun.adjs.insert({'noun': noun,'adj': adj})


def get_noun_occ_list(client, coll, coll2):
    """
    this function returns the list of dictionary of noun and its occurence in text
    :param client:client is the database instance.collection
    :return:
    """
    mapper = Code("""
                function(){
                    var key = {"noun":this.noun };
        	        emit(key,1);}
        	                        """)
    reducer = Code("""
                        function (key, values) {
                        var sum = 0;
                         values.forEach(function(value)
                        {
                            sum += 1
                        });
                return sum;  }
                    """)
    results = client[coll].map_reduce(mapper, reducer, coll2)
    return create_nouns_gen(results.find())


def create_nouns_gen(occ):
    for elm in occ:
        yield {"noun": elm['_id']['noun'],"count": elm['value']}


def get_adj_occ_list(client):
    """
    this function returns the list of dict of ajd and its occ
    :param client:client is the database instance.collection
    :return:
    """
    mapper = Code("""
            function(){
                var key = {"adj":this.noun };
    	        emit(key,1);} """)
    reducer = Code("""
                    function (key, values) {
                    var sum = 0;
                     values.forEach(function(value)
                    {
                        sum += 1
                    });
            return sum;  }
                """)
    results = client.noun.adjs.map_reduce(mapper, reducer, "adj.occ")
    return create_adj_gen(results.find())


def create_adj_gen(occ):
    for elm in occ:
        yield {"noun": elm['_id']['noun'],"count": elm['value']}


def get_noun_adj_list_occ(client):
    """
    this function returns the list of dict of noun , adj ,occ the table of
    noun adj grouped by  {noun, adj}
    :param client:
    :return:
    """
    mapper = Code("""
            function(){
                var key = {"noun":this.noun , "adj": this.adj};
    	        emit(key,1);}
    	                        """)
    reducer = Code("""
                    function (key, values) {
                    var sum = 0;
                     values.forEach(function(value)
                    {
                        sum += 1
                    });
            return sum;  }
                """)
    results = client.noun.adjs.map_reduce(mapper, reducer, "noun.adj.occ")
    return create_noun_adj_gen(results.find())


def create_noun_adj_gen(occ):
    for elm in occ:
        yield {"noun": elm['_id']['noun'],"adj": elm['_id']['adj'],"pmi": elm['value']}


def get_noun_occ(noun_occ_list, noun):
    """
     this function takes the list of {noun,occ} and an noun and returns the occ of the giving noun
    :param noun_occ_list:
    :param noun:
    :return:
    """
    dic = next(item for item in noun_occ_list if item["noun"] == noun)
    return dic['count']


def get_adj_occ(adj_occ_list, noun):
    """
    this function takes the list of {adj,occ} and an adj and returns the occ of the giving adj
    :param adj_occ_list:
    :param noun:
    :return:
    """
    dict = next(item for item in adj_occ_list if item["noun"] == noun )
    return dict['count']


def create_noun_adj_pmi_collection(database, noun_adj_occ_list, noun_occ_list, adj_occ_list):
    """this function is used to update the PMI column for each couple (noun,adj)"""
    names = database.collection_names()
    if "nounadj" in names:
        database.nounadj.drop()
        for dic in noun_adj_occ_list:
            dic["pmi"] = calculate_pmi(get_noun_occ(noun_occ_list, dic["noun"]),
                                        get_adj_occ(adj_occ_list, dic["adj"]),
                                        dic["pmi"])
    database.nounadj.insert(noun_adj_occ_list)
    return database.nounadj.find()

##############################################################
################# funtions for NOUN/NOUN pairs #############
##############################################################


def store_noun_noun(db, noun, adj):
    db.noun.rnoun.insert({'noun': noun,'rnoun': adj})


def get_rnoun_occ_list(client):
    """
    this function returns the list of dict of ajd and its occ
    :param client:
    :return:
    """
    mapper = Code("""
            function(){
                var key = {"rnoun":this.rnoun };
    	        emit(key,1);} """)
    reducer = Code("""
                    function (key, values) {
                    var sum = 0;
                     values.forEach(function(value)
                    {
                        sum += 1
                    });
            return sum;  }
                """)
    results = client.nouns.nouns.map_reduce(mapper, reducer, "rnoun.occ")
    nounocc = create_adj_gen(results.find())
    return nounocc


def create_rnoun_gen(occ):
    for elm in occ:
        yield   {"rnoun": elm['_id']['rnoun'],
             "count": elm['value']}


def get_noun_rnoun_list_occ(client):
    """
    this function returns the list of dict of noun , adj ,occ the table of
    noun adj grouped by  {noun, adj}
    :param client:
    :return:
    """
    mapper = Code("""
            function(){
                var key = {"noun":this.noun , "rnoun": this.rnoun};
    	        emit(key,1);}
    	                        """)
    reducer = Code("""
                    function (key, values) {
                    var sum = 0;
                     values.forEach(function(value)
                    {
                        sum += 1
                    });
            return sum;  }
                """)
    results = client.nouns.nouns.map_reduce(mapper, reducer, "noun.rnoun")
    return create_noun_rnoun_gen(results.find())


def create_noun_rnoun_gen(occ):
    for elm in occ:
        yield {"noun": elm['_id']['noun'], "rnoun": elm['_id']['rnoun'],
             "pmi": elm['value']}


def get_rnoun_occ(rnoun_occ_list, noun):
    """
    this function takes the list of {adj,occ} and an adj and returns the occ of the giving adj
    :param adj_occ_list:
    :param noun:
    :return:
    """
    dic = next(item for item in rnoun_occ_list if item["rnoun"] == noun)
    return dic['count']


def create_noun_noun_pmi_collection(database, noun_rnoun_occ_list, noun_occ_list, rnoun_occ_list):
    """this function is used to update the PMI column for each couple (noun,adj)"""
    names = database.collection_names()
    if "nouns" in names:
        database.nouns.drop()
        for dic in noun_rnoun_occ_list:
            dic["pmi"] = calculate_pmi(get_noun_occ(noun_occ_list, dic["noun"]),
                                        get_adj_occ(rnoun_occ_list, dic["rnoun"]),
                                        dic["pmi"])
    database.nouns.insert(noun_rnoun_occ_list)
    return database.nouns.find()
    # def get_subject_vector(db,subject):
    # def get_object_vector(db,object):
    # def get_predicate_vector(db,predicate):
    # def calculate_PMI(db):
    # def insert_sop(db):


def create_noun_list(db):
  nouns = db.nouns.aggregate([{"$group": {"_id": "$noun", "nouns": {"$push": "$rnoun"},
                                         "pmis": {"$push": "$pmi"}}}])
  for i in nouns:
    nn = i['_id']
    sub_list = []
    for noun, pmi in zip(i['nouns'], i['pmis']):
        elm = {"noun": noun, "pmi": pmi}
        sub_list.append(elm)
    yield ({"nouns": sub_list, "Noun": nn})


def create_noun_sorted_list(db):
    nouns = create_noun_list(db)
    for i in nouns:
        agents = [item["predicate"] for item in list(db.sop.find({"subject":i["Noun"][0]},{"predicate": 1}))]
        patients = [item["predicate"] for item in list(db.sop.find({"object":i["Noun"][0]},{"predicate": 1}))]
        adjs = [item["adj"] for item in list(db.nounadj.find({"noun":i["Noun"][0]},{"adj":1,"pmi":1}))]
        yield {"list_nouns":sorted(i["nouns"], key=lambda x: x['pmi'], reverse=True)[:10],"Noun": i["Noun"],
              "agent": agents,"patients":patients,"list_adjs":adjs}








