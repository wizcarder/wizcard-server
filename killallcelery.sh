ps auxww | grep 'wizcard worker' | awk '{print $2}' | xargs kill -9
