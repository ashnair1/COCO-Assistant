class CatRemapper:
    def __init__(self, cat1, cat2):
        """
        Target category list needs to be remapped to
        reference category list.

        The following are the three cases to be considered:
        *******************************************************

        Case 1: When cat1 and cat2 overlap and cat2 has no new
                categories

        cat1: [{'id': 1, 'name': 'A'},
               {'id': 2, 'name': 'B'},
               {'id': 3, 'name': 'C'}]

        cat2: [{'id': 1, 'name': 'B'},
               {'id': 2, 'name': 'C'},
               {'id': 3, 'name': 'A'}]

        result: [{'id': 1, 'name': 'A'},
                 {'id': 2, 'name': 'B'},
                 {'id': 3, 'name': 'C'}]

         with

        overlap: {1:2, 2:3, 3:1}
        newcat : {}

        *******************************************************

        Case 2: When cat1 and cat2 overlap & cat2 has new
                categories.

        cat1: [{'id': 1, 'name': 'A'},
               {'id': 2, 'name': 'B'},
               {'id': 3, 'name': 'C'}]

        cat2: [{'id': 1, 'name': 'B'},
               {'id': 2, 'name': 'A'},
               {'id': 3, 'name': 'F'}]

        result: [{'id': 1, 'name': 'A'},
                 {'id': 2, 'name': 'B'},
                 {'id': 3, 'name': 'C'},
                 {'id': 4, 'name': 'F'}]

        with

        overlap: {1:2, 2:1}
        newcat : {3:4}

        *******************************************************

        Case 3: When cat1 and cat2 don't overlap

        cat1: [{'id': 1, 'name': 'A'},
               {'id': 2, 'name': 'B'},
               {'id': 3, 'name': 'C'}]

        cat2: [{'id': 1, 'name': 'D'},
               {'id': 2, 'name': 'E'},
               {'id': 3, 'name': 'F'}]

        result: [{'id': 1, 'name': 'A'},
                 {'id': 2, 'name': 'B'},
                 {'id': 3, 'name': 'C'},
                 {'id': 4, 'name': 'D'},
                 {'id': 5, 'name': 'E'},
                 {'id': 6, 'name': 'F'}]

        with

        overlap: {}
        newcat : {1:4, 2:5, 3:6}

        :param cat1: Reference category list of dicts
        :param cat2: Target category list of dicts
        """

        self.refcat = cat1
        for c in self.refcat:
            c["name"] = c["name"].lower()

        self.cat1 = self.result = self.generate_id_map(cat1)
        self.cat2 = self.generate_id_map(cat2)

    def remap(self, ann):
        rescat, overlap_dict, newcat_dict = self.remap_cats()
        # Modify annotations
        new_ann = self.remap_annotations(ann, overlap_dict, newcat_dict)
        return rescat, new_ann

    def remap_cats(self):
        """
        Check if the reference and target category lists overlap
        and remap them as necessary.

        :return: result: new category list
        :return: overlap_dict: mapping of overlapping categories
        :return: newcat_dict: mapping of new categories

        """
        c1 = list(self.cat1.keys())
        c2 = list(self.cat2.keys())
        diff = sorted(list(set(c2) - set(c1)))

        newcat_dict = {}
        overlap_dict = {}
        res = []
        if diff:
            # New categories
            for i, d in enumerate(diff):
                newcat_dict[self.cat2[d]] = len(c1) + i + 1
                self.result[d] = len(c1) + i + 1
                del self.cat2[d]

            for k, v in self.result.items():
                res.append({"id": v, "name": k})

        for k, v in self.cat1.items():
            try:
                overlap_dict[self.cat2[k]] = v
            except KeyError:
                continue

        if res:
            # Return updated reference category list
            result = res
        else:
            # Return original reference category list
            result = self.refcat

        return result, overlap_dict, newcat_dict

    def remap_annotations(self, ann, overlaps, new_cats):
        """
        Remaps the annotation where overlapping category ids
        are mapped to reference category ids and new categories
        are given new ids.

        :param ann: annotation being modified (dict)
        :param overlaps: mapping of overlapping categories
        :param new_cats: mapping of new categories
        :return:
        """

        for a in ann:
            cat_id = a["category_id"]
            # The category is either new or exists in the reference annotation
            if cat_id in new_cats:
                a["category_id"] = new_cats[a["category_id"]]
            else:
                a["category_id"] = overlaps[a["category_id"]]
        return ann

    def generate_id_map(self, cat):
        c = [[i["name"].lower(), i["id"]] for i in cat]
        keys = [i[0] for i in c]
        values = [i[1] for i in c]
        idmap = dict(zip(keys, values))
        return idmap
