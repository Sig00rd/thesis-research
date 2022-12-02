# majority of this code was taken from https://github.com/olsgaard/Japanese_nlp_scripts
# below is copyright notice

# Copyright (c) 2014-2016, Mads sørensen Ølsgaard, olsgaard.dk
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import enum

class CharType(enum.Enum):
    OTHER = "OTHER"
    ALPHABET = "ALPHABET"
    HIRAGANA = "HIRAGANA"
    KATAKANA = "KATAKANA"
    DIGIT = "DIGIT"
    KANJI = "KANJI"
    END_QUOTE = "END QUOTE"
    TOOTEN = "TOOTEN"
    KUTEN = "KUTEN"
    EXCLAMATION_MARK = "EXCLAMATION MARK"
    QUESTION_MARK = "QUESTION MARK"

def get_char_type(c):
	# find the type of a unicode character
	# Adapted from KyTea
	
    if(len(c) == 0):
        return CharType.OTHER
    val = ord(c)

    # 、 ､
    # if val in (0x3001, 0xFF64):
    if val == 0x3001:
        return CharType.TOOTEN

    # 。｡
    # if val in (0x3002, 0xFF61):
    if val == 0x3002:
        return CharType.KUTEN

    # 」and 』and ｣
    # if val in (0x300D, 0x300F, 0xFF63):
    if val == 0x300D:
        return CharType.END_QUOTE

    # ！
    if val == 0xFF01:
        return CharType.EXCLAMATION_MARK
    
    # ？
    if val  == 0xFF1F:
        return CharType.QUESTION_MARK
    

	# Basic latin uppercase, basic latin lowercase
	# Full width uppercase, full width lowercase
    if (0x41 <= val <= 0x5A) or (0x61 <= val <= 0x7A) or (0xFF21 <= val <= 0xFF3A) or (0xFF41 < val < 0xFF5A):
        return CharType.ALPHABET

	# hiragana (exclude repetition characters)
    if (0x3040 <= val <= 0x3096):
        return CharType.HIRAGANA

	# full width (exclude center dot), half width
    if (0x30A0 <= val <= 0x30FF and val != 0x30FB) or (0xFF66 <= val <= 0xFF9F):
        return CharType.KATAKANA

	# basic latin digits
    if (0x30 <= val <= 0x39) or (0xFF10 <= val <= 0xFF19):
        return CharType.DIGIT

	# CJK Unified Ideographs
    if ((0x3400 <= val <= 0x4DBF)  # CJK Unified Ideographs Extension A
		   or (0x4E00 <= val <= 0x9FFF) # CJK Unified Ideographs
		   or (0xF900 <= val <= 0xFAFF) # CJK Compatibility Ideographs
			#|| (0x1F200 <= val <= 0x1F2FF) # Enclosed Ideographic Supplement
		   or (0x20000 <= val <= 0x2A6DF) # CJK Unified Ideographs Extension B
		   or (0x2A700 <= val <= 0x2B73F) # CJK Unified Ideographs Extension C
		   or (0x2B740 <= val <= 0x2B81F) # CJK Unified Ideographs Extension D
		   or (0x2F800 <= val <= 0x2FA1F)): # CJK Compatibility Ideographs Supplement
        return CharType.KANJI
    return CharType.OTHER

if __name__=="__main__":
	# text = '初めての駅 自由が丘の駅で、大井町線から降りると、ママは、トットちゃんの手を引っ張って、改札口を出ようとした。'
    text = "、､。｡」』｣？！"
    print('original text:\t', text)
    print('character classes:\t', ' '.join([get_char_type(c).value for c in text]))