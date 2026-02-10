#include<iostream>

class Solution{
    public:
    void set_bit(uint32_t &reg, int n){
        reg |= (1<<n);
    }
    void clear_bit(uint32_t reg, int n){
        reg &= ~(1<<n);
    }
};

int main(){
    Solution obj;
    uint32_t reg = 0x01;
    obj.set_bit(reg, 5);
    std::cout << "After setting bit 5: " << std::hex << reg << std::endl;
    
    obj.clear_bit(reg, 0);
    std::cout << "After clearing bit 0: " << std::hex << reg << std::endl;
    return 0;


}