def compare_and_choose(response1, response2):
    resp1_weight = 0
    resp2_weight = 0
    
    # if an array, convert to comma separated string
    if isinstance(response1, list):
        response1 = ','.join(response1)
        
    if isinstance(response2, list):
        response2 = ','.join(response2)
    
    # check how many commas in response1,2
    resp1_commas = response1.count(',')
    resp2_commas = response2.count(',')
    
    # check how many decimals in response1,2
    resp1_decimals = response1.count('.')
    resp2_decimals = response2.count('.')
    
    # if one response has more commas than the other, add 1 weight
    if resp1_commas > resp2_commas:
        resp1_weight += 1
        
    if resp2_commas > resp1_commas:
        resp2_weight += 1
        
    # if one response has more decimals than the other, add 2 weight
    if resp1_decimals > resp2_decimals:
        resp1_weight += 2
        
    if resp2_decimals > resp1_decimals:
        resp2_weight += 2
        
    # split by commas
    resp1_split = response1.split(',')
    resp2_split = response2.split(',')
    
    # for each split in response1, check if the split index exists in response2 and if so get a character difference between the splits
    for i, split in enumerate(resp1_split):
        if i >= len(resp2_split):
            break
            
        # if the split contains 2+ more characters in response1 than response2, add 1 weight to response2
        if len(split) - len(resp2_split[i]) >= 2:
            resp2_weight += 1
            
        # if the split contains 2+ more characters in response2 than response1, add 1 weight to response1
        if len(resp2_split[i]) - len(split) >= 2:
            resp1_weight += 1
            
        # if the split contains 2 or less characters (excluding decimals) in response1, add 1 weight to response2
        if len(split.replace('.', '')) <= 2:
            resp2_weight += 2
            
        # if the split contains 2 or less characters (excluding decimals) in response2, add 1 weight to response1
        if len(resp2_split[i].replace('.', '')) <= 2:
            resp1_weight += 2
            
        # if neither response has a decimal, add 1 weight to the one wirh less characters
        if '.' not in split and '.' not in resp2_split[i]:
            if len(split) < len(resp2_split[i]):
                resp1_weight += 1
            else:
                resp2_weight += 1
            
    # convert comma separated string back to list
    if ',' in response1:
        response1 = response1.split(',')
        
    if ',' in response2:
        response2 = response2.split(',')
            
    # if one response has more weights than the other, return the response with the most weight
    if resp1_weight > resp2_weight:
        return response1
    
    if resp2_weight > resp1_weight:
        return response2
    
    # if the weights are equal, return response1
    return response1

def compare_and_choose_new(*responses):
    # Initialize a list to store the weights for each response
    weights = []

    # Helper function to process each response and calculate its weight
    def calculate_weight(response):
        weight = 0
        
        # if the response is a list, convert to a comma-separated string
        if isinstance(response, list):
            response = ','.join(response)
        
        # check how many commas in response
        commas = response.count(',')
        
        # check how many decimals in response
        decimals = response.count('.')
        
        # check if more commas or decimals than others to assign weight
        weight += commas  # Increase weight based on the number of commas
        weight += 2 * decimals  # Increase weight based on the number of decimals
        
        # split by commas to compare individual parts
        split_response = response.split(',')
        
        for i, part in enumerate(split_response):
            # Add weight based on part length
            if len(part.replace('.', '')) <= 2:
                weight += 2  # Small parts get more weight
                
            # Compare lengths of current part with the previous part (if any)
            if i > 0:
                prev_part = split_response[i-1]
                if len(part) - len(prev_part) >= 2:
                    weight += 1  # Add weight if part is much longer
                
                if len(prev_part) - len(part) >= 2:
                    weight += 1  # Add weight if previous part is much longer
        
        return weight
    
    # Calculate weight for each response
    for response in responses:
        weights.append(calculate_weight(response))
    
    # Find the response with the maximum weight
    max_weight = max(weights)
    best_response = responses[weights.index(max_weight)]
    
    return best_response
