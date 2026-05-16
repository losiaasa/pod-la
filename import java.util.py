import java.util.*;

public class Solution {
    public int lengthOfLongestSubstring(String s) {
        int n = s.length();
        int maxLength = 0;
        Set<Character> set = new HashSet<>();
        int left = 0;

        for (int right = 0; right < n; right++) {
            // If the character is already in the set, remove characters from the left
            // until the duplicate is removed
            while (set.contains(s.charAt(right))) {
                set.remove(s.charAt(left));
                left++;
            }
            // Add the current character to the set
            set.add(s.charAt(right));
            // Update the maximum length
            maxLength = Math.max(maxLength, right - left + 1);
        }

        return maxLength;
    }

    public static void main(String[] args) {
        Solution solution = new Solution();
        
        // Test cases
        String[] testStrings = {"abcabcbb", "bbbbb", "pwwkew", "", "a", "dvdf"};
        
        for (String s : testStrings) {
            int result = solution.lengthOfLongestSubstring(s);
            System.out.println("Input: \"" + s + "\", Output: " + result);
        }
    }
}   