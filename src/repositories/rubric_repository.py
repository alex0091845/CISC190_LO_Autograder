class RubricRepository:
    def __init__(self):
        # rubric id to rubric?
        self.id_to_rubric: dict = {}
    
    def has_rubric(self, id: str):
        return id in self.id_to_rubric
    
    def get_rubric(self, id: str):
        return self.id_to_rubric.get(id, None)

    def _process_and_cache_rubric(self, rubric_data: list | None, assignment_id: str) -> None:
        """Process and cache the rubric data for a specific learning outcome (LO).
        Each is formatted as:
        ```
        {
            'LO Name': {
                'Criterion Description': {
                    'id': criterion_id,
                    'points': max_points,
                    'ratings': {
                        points_0: 'rating_id_0',
                        points_1: 'rating_id_1', 
                    }                     
                }
            },
        }
        ```
        For example:
        ```
        {
            'LO 1: Variables': {
                'M1 Draw My Name': {
                    'id': '12345',
                    'points': 5,
                    'ratings': {
                        0: 'rat1',
                        3: 'rat2',
                        5: 'rat3'
                    }
                },
                'M1 Share: Draw My Name': {
                    'id': '67890',
                    'points': 5,
                    'ratings': {
                        0: 'rat4',
                        3: 'rat5',
                        5: 'rat6'
                    }
                },
                ...
            }
        }
        ```
        The reason for this format is so that when updating the rubric assessment,
        it's easy to look up each field and value. Specifically, we need the LO name,
        the criterion id, the points, and the rating ID for each criterion.
        
        It's easy to look up each criterion by the LO name and criterion description,
        like: `self.lo_to_rubric[lo_name][criterion_desc]`. This is because the criterion
        description happens to be the assignment name. We can then also easily get the
        grade (complete, incomplete, N/A) via the assignment name in `Assignments.py`.

        Once looked up, since an assignment is either complete or incomplete, and we know
        the max points for that criterion/assignment, we can directly set the points to either
        max points (complete) or 0 (incomplete). Then, based on how many points we set, we can
        get the rating ID from the `ratings` key. This allows us to get the points and the rating ID.

        Args:
            rubric_data: The list of rubric criteria dictionaries from the assignment.
            lo_name: The name of the learning outcome (LO).
        Returns:
            None
        """
        for criterion in rubric_data or []:
            criterion_id = criterion.get('id', '')
            desc = criterion.get('description', '')
            points = criterion.get('points', 0)
            criterion_ratings = criterion.get('ratings', [])

            ratings = {rating['points']: rating['id'] for rating in criterion_ratings}

            # if not there, create one
            if self.id_to_rubric.get(assignment_id) is None:
                self.id_to_rubric[assignment_id] = {}
            
            # add description to points map
            self.id_to_rubric[assignment_id][desc] = {
                'id': criterion_id,
                'points': points,
                'ratings': ratings
            }