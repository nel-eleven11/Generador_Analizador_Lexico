def combine_formatted_regex(formatted_regex_list):

    combined_regex = ""

    for regex in formatted_regex_list:
        print(f"Reafing regex: {regex}")
        new_string = f"({regex})|"

        combined_regex = combined_regex + new_string

        #print(f"combined regex progress {combined_regex}")
    
    final_combined_regex = combined_regex[:-1]

    print(f"Final combined regex: {final_combined_regex}")
    return final_combined_regex