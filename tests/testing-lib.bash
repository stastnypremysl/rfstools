
generate_file()(
  tmp=$(mktemp)
  dd if=/dev/urandom of=$tmp bs=2048 count=65536
  echo $tmp
)

print_test_start(){
  printf "Starting test \e[1m$test\e[0m...\n"
}

print_test_fail(){
  printf "\e[31mTEST $test FAILED\e[0m \n\n"
  exit 1
}

print_test_succeeded(){
  printf "Test $test succeeded\n\n"
  test=NAN
}

cp_test(){
  test=cp_test
  print_test_start
  
  (
    l1_file=$(generate_file)
    trap "rm $l1_file" EXIT

    l2_file=$l1_file.transmit
 
  ) || print_test_fail
  print_test_succeeded
    
}
