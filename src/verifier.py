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


def read_matching(filename, n):
    """
    Reads and parses the matching output file.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Remove empty lines and strip whitespace
    lines = [line.strip() for line in lines if line.strip()]
    
    if len(lines) != n:
        raise ValueError(f"Expected {n} matching pairs, got {len(lines)}")
    
    matching = [None] * n
    
    for line in lines:
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"Invalid matching line format: '{line}'")
        
        hospital = int(parts[0]) - 1  # Convert to 0-indexed
        student = int(parts[1]) - 1   # Convert to 0-indexed
        
        if hospital < 0 or hospital >= n:
            raise ValueError(f"Invalid hospital index: {hospital + 1}")
        if student < 0 or student >= n:
            raise ValueError(f"Invalid student index: {student + 1}")
        
        matching[hospital] = student
    
    return matching


def check_validity(n, matching):
    """
    Checks if the matching is valid (each hospital and student matched exactly once).
    """
    # Check that all hospitals have a match
    for h in range(n):
        if matching[h] is None:
            return False, f"INVALID: Hospital {h + 1} is not matched"
    
    # Check for duplicate students (each student matched at most once)
    student_matched_to = {}
    for h in range(n):
        s = matching[h]
        if s in student_matched_to:
            return False, f"INVALID: Student {s + 1} is matched to both Hospital {student_matched_to[s] + 1} and Hospital {h + 1}"
        student_matched_to[s] = h
    
    # Check that all students are matched (since n hospitals and n students, and no duplicates)
    if len(student_matched_to) != n:
        # Find which students are not matched
        all_students = set(range(n))
        matched_students = set(student_matched_to.keys())
        unmatched = all_students - matched_students
        unmatched_list = [s + 1 for s in unmatched]
        return False, f"INVALID: Students {unmatched_list} are not matched to any hospital"
    
    return True, ""


def check_stability(n, hospital_prefs, student_prefs, matching):
    """
    Checks if the matching is stable (no blocking pairs exist).
    """
    # Create reverse mapping: which hospital is each student matched to?
    student_match = [None] * n
    for h in range(n):
        s = matching[h]
        student_match[s] = h
    
    # Create ranking matrices for O(1) preference lookups
    # hospital_ranking[h][s] = rank of student s in hospital h's preference list
    hospital_ranking = []
    for h in range(n):
        ranking = [0] * n
        for rank, student in enumerate(hospital_prefs[h]):
            ranking[student] = rank
        hospital_ranking.append(ranking)
    
    # student_ranking[s][h] = rank of hospital h in student s's preference list
    student_ranking = []
    for s in range(n):
        ranking = [0] * n
        for rank, hospital in enumerate(student_prefs[s]):
            ranking[hospital] = rank
        student_ranking.append(ranking)
    
    # Check all possible (hospital, student) pairs for blocking pairs
    for h in range(n):
        for s in range(n):
            current_student = matching[h]  # Who hospital h is currently matched to
            current_hospital = student_match[s]  # Who student s is currently matched to
            
            # Skip if already matched to each other
            if current_student == s:
                continue
            
            # Check if hospital h prefers student s over their current match
            if hospital_ranking[h][s] < hospital_ranking[h][current_student]:
                # Hospital h prefers s over current match
                # Now check if student s prefers hospital h over their current match
                if student_ranking[s][h] < student_ranking[s][current_hospital]:
                    # Student s also prefers h over current match
                    # This is a blocking pair!
                    return False, f"UNSTABLE: Blocking pair (Hospital {h + 1}, Student {s + 1})"
    
    return True, ""


def main():
    """
    Main entry point for the verifier program.
    Reads preferences and matching, checks validity and stability.
    """
    if len(sys.argv) != 3:
        print("Usage: python verifier.py <input_file> <matching_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    matching_file = sys.argv[2]
    
    try:
        # Read input preferences
        n, hospital_prefs, student_prefs = read_input(input_file)
        
        # Read proposed matching
        matching = read_matching(matching_file, n)
        
        # Check validity first
        is_valid, validity_msg = check_validity(n, matching)
        
        if not is_valid:
            # If invalid, no need to check stability
            print(validity_msg)
        else:
            # Only check stability if valid
            is_stable, stability_msg = check_stability(n, hospital_prefs, student_prefs, matching)
            
            if is_stable:
                print("VALID STABLE")
            else:
                print(stability_msg)
    
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid input format - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()