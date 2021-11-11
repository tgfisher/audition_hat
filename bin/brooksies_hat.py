#!/usr/bin/env python

import sys
import random
import time

USER_PROMPT = """
    \t.------------------------------------------------------------------------------
    \t| Would you like to:
    \t|\t[R]eturn this audition to the hat and get a new one.
    \t|\t[S]ubset return (e.g. S 1 3 <- 1st and 3rd excerpt) and get a new one.
    \t|\t[V]iew past auditions.
    \t|\t[L]ist remaining excerpt enumerations.
    \t|\t<Enter> to just take the next audition.
    \t|\t[Q]uit or [<Ctrl>-C]rap out.
    \t`------------------------------------------------------------------------------
    """
#    \t Please hit <Enter> after your choice:  

class hat():
    """
    TODO: save out current hat into text file.
    TODO: set a random seed so you can make a 'social' network of ppl
        taking the same 'random' auditions.
    TODO: catch subset returns out of index
    pw version
    """
    def __init__(self, n_excerpts, audition_length, ignore_list=[]):

        print(
            "Initializing with {} excerpts".format(n_excerpts) +
            " and an audition length of {}".format(audition_length)
        )

        assert audition_length <= n_excerpts, "audition length longer than number of excerpts getting put in your hat"

        self.n_excerpts = n_excerpts
        self.excerpts_in_hat = [num+1 for num in range(n_excerpts)]
        self.audition_length = audition_length
        self.ignore_list = ignore_list
        self.curr_audition = []
        self.__past_auditions__ = []
        self.__excerpt_idxs__ = []
        self.fresh_hat = True
        self.keep_drawing = True

    def generate_audition(self):
        self.__excerpt_idxs__ = [
            idx for idx in range(len(self.excerpts_in_hat))
        ]

        try:
            curr_audition_idxs = random.sample(
            self.__excerpt_idxs__,
            self.audition_length
            )

            curr_audition = [
            self.excerpts_in_hat.pop(idx) 
            for idx in sorted(curr_audition_idxs)[::-1]
            ]

            # shuffle
            random.shuffle(curr_audition)
            self.curr_audition = curr_audition[:]

            self.__past_auditions__ += [self.curr_audition]
        except ValueError as e:
            print("\nLast Audition!")
            n_extras_to_pad = self.audition_length - len(self.excerpts_in_hat)
            audition_padding = self.draw_n_from_past(n_extras_to_pad)
            
            self.add_to_hat(audition_padding)
            self.generate_audition()

        self.fresh_hat = False

    def add_to_hat(self, to_add):
        if isinstance(to_add, list):
            self.excerpts_in_hat += to_add
        else:
            self.excerpts_in_hat += [int(to_add)]

        self.excerpts_in_hat.sort()

    def view_n_remaining(self):
        print("n items remaining in hat {}".format(len(self.excerpts_in_hat)))

    def draw_n_from_past(self, n):
        if self.fresh_hat:
            print("No past to draw from, this is a fresh hat")
        else:
            past = [
                excerpt for audition
                in self.__past_auditions__ for excerpt in audition
            ]

            return random.sample(past, n)
        

    def ignore_list(self):
        return self.__ignore_list__
        
    def view_past(self):
        print("\nThese are your past auditions:")
        print("\t"+"\n\t".join([str(exc) for exc in self.__past_auditions__]))

    def _ordinal_str(self,ur_int):
        if int(ur_int) == 1:
            return "1st"
        elif int(ur_int) == 2:
            return "2nd"
        elif int(ur_int) == 3:
            return "3rd"
        else:
            return "{}th".format(int(ur_int))
        
    def prompt_audition(self):
        self.generate_audition()
        print("Dance!:".format(self.curr_audition))
        audition_enum = [num+1 for num in range(len(self.curr_audition))]
        audition_enum_strs = [
            self._ordinal_str(enum) + ": " + str(excerpt) for enum, excerpt
            in zip(audition_enum, this_hat.curr_audition)
        ]
        print("\t"+"\n\t".join(audition_enum_strs))
        print("\n")


    def user_interact(self):
        if self.fresh_hat:
            print("No auditions yet, can't interact. You need to generate_audition first.")
        elif self.fresh_hat is False:
            try:
                inputer = raw_input
            except NameError as e:
                print("(Ignore unless you are a developer) NameError: {}".format(e))
                print("\tNOTE: you are using python w/o raw_input, trying input")
                inputer = input
            user_in = inputer(
                USER_PROMPT + "\t Please hit <Enter> after your choice:  "
            )
            self._parse_return_str(user_in)


    def _parse_return_str(self,user_in_str):
        """
        This function parses the string collected by the user_interact method.
        """
        if user_in_str == "":
            self.prompt_audition()
        elif user_in_str.lower() == "r":
            self.add_to_hat(self.curr_audition)
            print("\n\nRETURNING: {}\n\n".format(self.curr_audition))
            time.sleep(1)
            self.prompt_audition()
        elif user_in_str.lower() == "v":
            self.view_past()
        elif user_in_str.lower() == "l":
            print(self.excerpts_in_hat)
        elif user_in_str.lower() == "q":
            self.excerpts_in_hat = []
        elif user_in_str.lower()[0] == "s":
            return_idxs = self._parse_subset_return_str(user_in_str)
            return_excerpts = [self.curr_audition[idx] for idx in return_idxs]
            self.add_to_hat(return_excerpts)
        else: #basic catch just goes on
            self.prompt_audition() 

    def _parse_subset_return_str(self, subset_user_in_str):
        """
        Parses the [S]ubset return string. must be of the form "s..."
        or "S...". Returns the indices of the [S]ubset to be returned
        from the current audition. This input requires a little extra 
        parsing.
        """
        assert subset_user_in_str.lower()[0] == "s", "This isn't a [S]ubset return request, wrong parser"
        split_ins = subset_user_in_str.split(" ")
        try:
            return [int(val)-1 for val in split_ins[1:]]
        except ValueError as e:
            print(
                "\n :-(( You are being sloppy, attempting to " +
                "fix ur dumb ass. :-))\n"
            )
            add_idxs = []
            for this_in in split_ins[1:]:
                try:
                    add_idxs += [int(this_in)-1] 
                except ValueError as e_again:
                    if this_in == "":
                        print("Note: Don't Need Trailing Space\n\n")
                        time.sleep(2)
                    else:
                        print(
                            "{} <-- integer? nah... failed to parse.".format(this_in)
                        )
                        time.sleep(2)
            return add_idxs 
if __name__ == "__main__":
    file_name = sys.argv[0]

    assert 3 <= len(sys.argv), "at minimum you need two inputs"

    n_excerpts = int(sys.argv[1])
    audition_length = int(sys.argv[2])

    ignore_list = []

    this_hat = hat(n_excerpts, audition_length, ignore_list) 
    
    this_hat.prompt_audition()
    while this_hat.excerpts_in_hat:
        this_hat.user_interact()
    this_hat.view_past()
