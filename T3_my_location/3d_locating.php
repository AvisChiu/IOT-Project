<?php
/**
 *这是在实际项目中收集归纳的算法，通过php实现或者由其他编程语言翻译成php
 *
 *by lina
 *version 1.0.0
 */
class LinaPHPAlgorithm
{

    /**
     * 矩阵相加
     * 
     * @param $arr1 一个二维数组，表示一个方阵
     * @param $arr2 一个二维数组，表示一个方阵
     * @return 一个二维数组，表示两矩阵相加的结果
     */
    public function getMatrixAdd($arr1,$arr2){
        if((count($arr1) != count($arr2))||(count($arr1[0]) != count($arr2[0])) ){
            return false;
        }
        for($i=0;$i < count($arr1);$i++){
            for($j=0;$j < count($arr1[0]);$j++){
                $arr1[$i][$j] = $arr1[$i][$j] + $arr2[$i][$j];
            }
        }
        return $arr1; 
    }

    /**
     * 矩阵相减
     * 
     * @param $arr1 一个二维数组，表示一个方阵
     * @param $arr2 一个二维数组，表示一个方阵
     * @return 一个二维数组，$arr1-$arr2
     */
    public function getMatrixSub($arr1,$arr2){
        if((count($arr1) != count($arr2))||(count($arr1[0]) != count($arr2[0])) ){
            return false;
        }
        for($i=0;$i < count($arr1);$i++){
            for($j=0;$j < count($arr1[0]);$j++){
                $arr1[$i][$j] = $arr1[$i][$j] - $arr2[$i][$j];
            }
        }
        return $arr1;
    }

    /**
     * 矩阵相乘
     * 
     * @param $arr1 一个二维数组，表示一个方阵
     * @param $arr2 一个二维数组，表示一个方阵
     * @return 一个二维数组，$arr1*$arr2
     */
    public function getMatrixMul($arr1,$arr2){
        if( count($arr1[0]) != count($arr2) ){
            return false;
        }

        for($i=0;$i < count($arr1);$i++){
            for($j=0;$j < count($arr2[0]);$j++){
                $res_arr[$i][$j] = 0;
                for($m = 0;$m < count($arr1[0]);$m++){
                    $res_arr[$i][$j] = $res_arr[$i][$j] + $arr1[$i][$m]*$arr2[$m][$j];
                }
                
            }
        }
        return $res_arr;
    }

    /**
     * G-J消元法求矩阵逆矩阵
     *
     * @param $arr 一个二维数组，表示一个方阵
     * @return 一个二维数组，表示输入数组的逆矩阵
     */
    public function getInverseMatrixByGJ($arr){
    	//只有方阵才有逆矩阵
    	if(!is_array($arr) || !is_array($arr[0]) || count($arr)!=count($arr[0]) ){
    		return false;
    	}
    	//结果矩阵
    	$res_arr = $arr;
    	for($i = 0;$i < count($arr);$i++){
    		for ($j=0; $j < count($arr); $j++) { 
    			if($i == $j){
    				$res_arr[$i][$j] = 1;
    			}else{
    				$res_arr[$i][$j] = 0;
    			}
    		}
    	}

    	for($i = 0;$i < count($arr);$i++){
    		$max = 0;
    		$max_ind = 0;
    		//寻找当前列的最大值
    		for($j = $i;$j < count($arr);$j++){
    			if(abs($arr[$i][$j]) >= $max){
    				$max_ind = $j;
                    $max = abs($arr[$i][$j]);
    			}
    		}

    		//把最大值移动到主对角线上
    		if($max_ind != $i){
	    		$a = $arr[$i];
	    		$arr[$i] = $arr[$max_ind];
	    		$arr[$max_ind] = $a;
	    		$a = $res_arr[$i];
	    		$res_arr[$i] = $res_arr[$max_ind];
	    		$res_arr[$max_ind] = $a;     			
    		}
    		
    		//对角线上的元素称为主元
    		$a = $arr[$i][$i];

    		//主元为0则为奇异矩阵，无逆矩阵
    		if($a == 0){
    			return false;
    		}

    		//将$arr主对角线上的元素化为1
    		for($j = $i;$j < count($arr);$j++){
    			$arr[$i][$j] = $arr[$i][$j]/$a;
    		}
    		for($j = 0;$j < count($arr);$j++ ){
    			$res_arr[$i][$j] = $res_arr[$i][$j]/$a;
    		}
    	
    		//将当前列非主对角线上的元素变为0
    		for($j = 0;$j < count($arr);$j++ ){
    			if($j != $i){
    				$c = $arr[$j][$i]/$arr[$i][$i];
    				for($k = 0;$k < count($arr);$k++){
    					$arr[$j][$k] = $arr[$j][$k] - $arr[$i][$k]*$c;
    					$res_arr[$j][$k] = $res_arr[$j][$k] - $res_arr[$i][$k]*$c;
    				}
    			}

    		}
    	}
        return  $res_arr;
    }

    /**
     * 平面三点定位
     *
     * @param $arr 一个二维数组，表示3个点的x,y坐标和到中心点的距离
     * @return $res_arr 一个一位数组，表示中心点的x,y
     */ 
    public function getPositionByThreePoint($arr){
        for($i = 0;$i < 2;$i++){
            for($j = 0;$j < 2;$j++){
                $arr1[$i][$j] = 2*($arr[0][$j] - $arr[$i+1][$j]);
            }
        } 

        for($i = 0;$i < 2;$i++){
            $arr2[$i][0] = pow($arr[0][0],2)+pow($arr[0][1],2);
            $arr2[$i][0] =$arr2[$i][0] - pow($arr[$i+1][0],2)-pow($arr[$i+1][1],2);
            $arr2[$i][0] =$arr2[$i][0] - pow($arr[0][2],2) + pow($arr[$i+1][2],2);
        }

        $arr1_1 = $this->getInverseMatrixByGJ($arr1);
        $arr2_2 = $this->getMatrixMul($arr1_1,$arr2);

        return $arr2_2;
    }

    /**
     * 三维空间四点定位
     *
     * @param $arr 一个二维数组，表示4个点的x,y,z坐标和到中心点的距离
     * @return $res_arr 一个一位数组，表示中心点的x,y,z
     */ 
    public function getPositionByFourPoint($arr){
        for($i = 0;$i < 3;$i++){
            for($j = 0;$j < 3;$j++){
                $arr1[$i][$j] = 2*($arr[0][$j] - $arr[$i+1][$j]);
            }
        } 

        for($i = 0;$i < 3;$i++){
            $arr2[$i][0] = pow($arr[0][0],2)+pow($arr[0][1],2)+pow($arr[0][2],2);
            $arr2[$i][0] =$arr2[$i][0] - pow($arr[$i+1][0],2)-pow($arr[$i+1][1],2)-pow($arr[$i+1][2],2);
            $arr2[$i][0] =$arr2[$i][0] - pow($arr[0][3],2) + pow($arr[$i+1][3],2);
        }

        $arr1_1 = $this->getInverseMatrixByGJ($arr1);
        $arr2_2 = $this->getMatrixMul($arr1_1,$arr2);

        return $arr2_2;  
    }

}