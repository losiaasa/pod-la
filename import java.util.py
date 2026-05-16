class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        n = len(s)
        max_length = 0
        char_set = set()
        left = 0

        for right in range(n):
            # If the character is already in the set, remove characters from the left
            # until the duplicate is removed
            while s[right] in char_set:
                char_set.remove(s[left])
                left += 1
            # Add the current character to the set
            char_set.add(s[right])
            # Update the maximum length
            max_length = max(max_length, right - left + 1)

        return max_length

if __name__ == "__main__":
    solution = Solution()
    
    # Test cases
    test_strings = ["abcabcbb", "bbbbb", "pwwkew", "", "a", "dvdf"]
    
    for s in test_strings:
        result = solution.lengthOfLongestSubstring(s)
        print(f'Input: "{s}", Output: {result}')