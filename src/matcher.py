import sys


def read_input(filename):
    """
    Reads and parses the input file containing hospital and student preferences.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Remove empty lines and strip whitespace
    lines = [line.strip() for line in lines if line.strip()]
    
    # First line is n
    n = int(lines[0])
    
    # Validate we have enough lines
    if len(lines) < 1 + 2 * n:
        raise ValueError(f"Expected {1 + 2*n} lines, got {len(lines)}")
    
    # Next n lines are hospital preferences (1-indexed in input, convert to 0-indexed)
    hospital_prefs = []
    for i in range(1, n + 1):
        prefs = [int(x) - 1 for x in lines[i].split()]  # Convert to 0-indexed
        if len(prefs) != n:
            raise ValueError(f"Hospital {i} preference list has {len(prefs)} entries, expected {n}")
        hospital_prefs.append(prefs)
    
    # Next n lines are student preferences (1-indexed in input, convert to 0-indexed)
    student_prefs = []
    for i in range(n + 1, 2 * n + 1):
        prefs = [int(x) - 1 for x in lines[i].split()]  # Convert to 0-indexed
        if len(prefs) != n:
            raise ValueError(f"Student {i-n} preference list has {len(prefs)} entries, expected {n}")
        student_prefs.append(prefs)
    
    return n, hospital_prefs, student_prefs


def gale_shapley(n, hospital_prefs, student_prefs):
    """
    Executes the hospital-proposing Gale-Shapley algorithm.
    """
    # Track which student each hospital is matched to (-1 = unmatched)
    hospital_match = [-1] * n
    
    # Track which hospital each student is matched to (-1 = unmatched)
    student_match = [-1] * n
    
    # Track next student to propose to for each hospital
    next_proposal = [0] * n
    
    # Create ranking matrix for students (for O(1) preference lookup)
    # student_ranking[s][h] = rank of hospital h in student s's preference list
    student_ranking = []
    for s in range(n):
        ranking = [0] * n
        for rank, hospital in enumerate(student_prefs[s]):
            ranking[hospital] = rank
        student_ranking.append(ranking)
    
    # Count total proposals (optional, for analysis)
    proposal_count = 0
    
    # Main algorithm loop
    while True:
        # Find an unmatched hospital that still has students to propose to
        free_hospital = -1
        for h in range(n):
            if hospital_match[h] == -1 and next_proposal[h] < n:
                free_hospital = h
                break
        
        # If no such hospital exists, we're done
        if free_hospital == -1:
            break
        
        # Get the next student on this hospital's preference list
        student = hospital_prefs[free_hospital][next_proposal[free_hospital]]
        next_proposal[free_hospital] += 1
        proposal_count += 1
        
        # If student is unmatched, tentatively accept
        if student_match[student] == -1:
            hospital_match[free_hospital] = student
            student_match[student] = free_hospital
        else:
            # Student is already matched, compare preferences
            current_hospital = student_match[student]
            
            # Student prefers new hospital if it has lower rank in their list
            if student_ranking[student][free_hospital] < student_ranking[student][current_hospital]:
                # Student prefers new hospital, reject current
                hospital_match[current_hospital] = -1
                hospital_match[free_hospital] = student
                student_match[student] = free_hospital
            # Otherwise student rejects new proposal (free_hospital stays unmatched)
    
    return hospital_match


def main():
    """
    Main entry point for the matching program.
    Reads input, runs algorithm, outputs results.
    """
    if len(sys.argv) != 2:
        print("Usage: python matcher.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        # Read input
        n, hospital_prefs, student_prefs = read_input(input_file)
        
        # Run Gale-Shapley algorithm
        matching = gale_shapley(n, hospital_prefs, student_prefs)
        
        # Output results (convert back to 1-indexed)
        for hospital in range(n):
            student = matching[hospital]
            print(f"{hospital + 1} {student + 1}")
    
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid input format - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()