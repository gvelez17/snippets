def score_match(afee_atty, matty):
    score = 0
    if DEBUG > 1:
        print "Scoring match between " + str(afee_atty) + '*********' + str(matty)
    if afee_atty.get('first') or afee_atty.get('last'):
        (f,m,l,s) = (afee_atty.get('first'), afee_atty.get('middle'), afee_atty.get('last'), afee_atty.get('suffix'))
    else:
        (f, m, l, s) = cleaners.decompose_name(afee_atty['firstname'] + ' ' + afee_atty['lastname'])
  
    # sometimes matty is from afee, sometimes direct from avvo or other source 
    if matty.get('first') or matty.get('last'):
         (ff, mm, ll, ss) = (matty['first'], matty['middle'], matty['last'], matty['suffix'])
    elif matty.get('firstname'):
         (ff, mm, ll, ss) = cleaners.decompose_name(matty['firstname'] + ' ' + matty['lastname'])
    elif matty.get('name'):
        (ff, mm, ll, ss) = cleaners.decompose_name(matty['name'])   
    else:
        return 0

    try:
        f = f.lower(); m = m.lower(); l = l.lower(); s = s.lower()
        ff = ff.lower(); mm = mm.lower(); ll = ll.lower(); ss = ss.lower
    except:
        pass

    # check avvo_url
    try:
        if (afee_atty.get('avvo') == matty.get('avvo_url') or afee_atty.get('avvo') == matty.get('avvo')):
            score += SCORES['avvo_url']
            if DEBUG:
                print "Have matching avvo url score is %f" % score
    except:
        pass

    # first names + middle
    if (f == ff):
        if (m or mm):  # have at least one middle name
            if (not m or not mm):   # only one has middle name
                score += SCORES['first_is_only']
            elif (len(m)>1 and m == mm):   # both have middle w/long match
                score += SCORES['first_and_full_middle']
            elif (m[0] == mm[0]):             # both have middle w/initial match
                score += SCORES['first_and_middle']
            else:                             # first match, middle mismatch
                score += SCORES['first_not_middle']
        else:
            score += SCORES['first_is_only']    # could rate this a little higher since neither have middle
    elif (f or ff):
        score += NEG_SCORES['not_first']

    if DEBUG:
        print "After first names score is %f" % score

    # last names + suffix
    if (l == ll):
        if (s == ss):
            score += SCORES['last_and_suffix'] * freq_mult(l)
        else:
            score += SCORES['last'] * freq_mult(l)
    else:
        if DEBUG:
            print " negative, %s not equal to %s " % (l, ll)
        score += NEG_SCORES['not_last']

    if DEBUG:
        print "After last names score is %f" % score

    # location: zip, city, state - only one plus, from most specific match
    if ( both_match(afee_atty, matty, 'zipcode')):
        score += SCORES['zip']
    elif ( both_match(afee_atty, matty, 'city')):
        score += SCORES['city']
    elif ( is_nearby(afee_atty, matty) ):
        score += SCORES['nearby']
    elif ( both_match(afee_atty, matty, 'state')):
        score += SCORES['state']


    # nonblank exact address match
    if ( both_match(afee_atty, matty, 'address1')):
        score += SCORES['address']

    # nonblank exact phone match
    if ( both_match(afee_atty, matty, 'phone')):
        score += SCORES['phone']

    # penalize explicit mismatches
    if ( both_have(afee_atty, matty, 'state') and afee_atty['state'] != matty['state']):
        score += NEG_SCORES['not_state']
    if ( both_have(afee_atty, matty, 'city') and afee_atty['city'] != matty['city']):
        score += NEG_SCORES['not_city']

    if ( both_have(afee_atty, matty, 'phone') and afee_atty['phone'] != matty['phone']):
        score += NEG_SCORES['not_phone']

    if ( both_have(afee_atty, matty, 'suffix') and afee_atty['suffix'] != matty['suffix']):
        score += NEG_SCORES['not_suffix']
    

    if DEBUG:
        print "After location score is %f" % score

    if (both_have(afee_atty, matty, 'firm') and afee_atty['firm'].title() == matty['firm'].title()):
        score += SCORES['lawfirm'] 

    return score
