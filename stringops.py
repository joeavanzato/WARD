import fs_interaction

class string_operator():
    def __init__(self):
        self.log_buddy = fs_interaction.log_writer()

    def split_items(self,values): #Split REGV into key:value pair -> think about building straight or still using CSV
        item_dict = {}
        self.log_buddy.write_log("Execution","SPLITTING "+values+" ON ;")
        try:
            item_list = values.split(";")
        except:
            self.log_buddy.write_log("Error", "ERROR SPLITTING "+item_list+" ON ; - MALFORMED INPUT MISSING ';'")
            tb = traceback.format_exc()
            self.log_buddy.write_log("Error",str(tb))
            error = 1
            return error
        x = 0
        len_list = len(item_list)
        while x < len(item_list):
            item_dict[item_list[x]] = item_list[x+1]
            x = x + 2
        return item_dict

    def get_longest(self,data): #Calculate longest string in list
        self.log_buddy.write_log("Execution","GETTING LONGEST FROM "+str(data))
        longest = 0
        for name in data:
            length = len(name)
            if length > longest:
                longest = len(name)
                longest_name = name
        self.log_buddy.write_log("Execution","LONGEST FOUND AS "+longest_name)
        return longest

    def mod_difference(self,data, longest): #Calculate difference in length between passed string and integer from 'get_longest()', append spaces to evenout
        self.log_buddy.write_log("Execution","CALCULATING LENGTH DIFFERENCE BETWEEN "+str(data)+" AND "+str(longest))
        difference = longest - len(data)
        self.log_buddy.write_log("Execution","DIFFERENCE FOUND AS "+str(difference))
        desc = data
        for x in range(0, difference):
            desc = " "+desc
        self.log_buddy.write_log("Execution","STRING MODIFIED FROM "+data+" TO "+desc)
        return desc

