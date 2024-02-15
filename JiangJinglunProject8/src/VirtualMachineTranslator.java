import java.io.*;
import java.util.*;
import java.nio.file.*;

public class VirtualMachineTranslator{

  private static final String[] ARITHMETIC_COMMANDS = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"};

  private static final String[] MEMORY_ACCESS_COMMANDS = {"push", "pop"};

  private static final String[] PROGRAM_FLOW_COMMANDS = {"label", "goto", "if-goto"};

  private static final String[] FUNCTION_CALLING_COMMANDS = {"function", "call", "return"};

  private static final String[] SEGMENT_MAP = {"argument", "local", "this", "that"};

  private static final String[] TEMP_SEGMENTS = {"0", "1", "2", "3", "4", "5", "6", "7"};

  private static final String STATIC_SEGMENT = "static";

  private static final String POINTER_SEGMENT = "pointer";

  private static final String CONSTANT_SEGMENT = "constant";

  private static int labelCounter = 0;

  private static int returnCounter = 0;

  /* 
    Main function that takes in the input file
    Convert the inputs into a list of strings
    Call the translateVMtoASM function
  */
  public static void main(String[] args){
    if (args.length == 0){
      System.err.println("Usage: java VirtualMachineTranslator <input-file>");
      return;
    }

    String inputFileName = args[0];
    File inputFile = new File(inputFileName);

    if (inputFile.isFile()){
      translateFile(inputFileName);
    } else if (inputFile.isDirectory()){
      translateDirectory(inputFile);
    } else{
      System.err.println("Invalid input: " + inputFileName);
    }

    // String inputFileName = args[0];
    // String outputFileName = inputFileName.replace(".vm", ".asm");

    // try{
    //   List<String> commands = Files.readAllLines(Paths.get(inputFileName));
    //   List<String> translatedCommands = translateVMtoASM(commands);

    //   String bootstrapCode = generateBoostrapCode();
    //   translatedCommands.add(0, bootstrapCode);

    //   writeLinesToFile(outputFileName, translatedCommands);

    //   System.out.println("Translation completed. Output file: " + outputFileName);
    // } catch (IOException e){
    //   System.err.println("Error reading input file: " + e.getMessage());
    // }
  }

  /*
    Translate file logic which translates the file.
  */
  private static void translateFile(String inputFileName) {
    String outputFileName = inputFileName.replace(".vm", ".asm");
    String fileNameWithoutExtension = new File(inputFileName).getName().replaceFirst("[.][^.]+$", "");

    try {
      List<String> commands = Files.readAllLines(Paths.get(inputFileName));
      List<String> translatedCommands = translateVMtoASM(commands, fileNameWithoutExtension);

      writeLinesToFile(outputFileName, translatedCommands);

      System.out.println("Translation completed. Output file: " + outputFileName);
    } catch (IOException e) {
      System.err.println("Error reading input file: " + e.getMessage());
    }
  }

  /*
    When the input is directory, direct to the translateDirectory logic.
  */
  private static void translateDirectory(File inputFile) {
      String[] files = inputFile.list((dir, name) -> name.endsWith(".vm"));
      String parentDirectoryName = inputFile.getName();
      String parentDirectoryPath = inputFile.getPath();

      String bootstrapCode = generateBoostrapCode();
      List<String> allTranslatedCommands = new ArrayList<>();

      for (String file : files) {
          String fileNameWithoutExtension = new File(file).getName().replaceFirst("[.][^.]+$", "");

          try {
              List<String> commands = Files.readAllLines(Paths.get(parentDirectoryPath, file));
              List<String> translatedCommands = translateVMtoASM(commands, fileNameWithoutExtension);
              allTranslatedCommands.addAll(translatedCommands);
          } catch (IOException e) {
              System.err.println("Error reading input file: " + e.getMessage());
          }
      }

      allTranslatedCommands.add(0, bootstrapCode);

      String outputFileName = parentDirectoryPath + File.separator + parentDirectoryName + ".asm";
      writeLinesToFile(outputFileName, allTranslatedCommands);
      System.out.println("Translation completed. Output file: " + outputFileName);
  }

  /*
    The bootstrap code generator
  */
  private static String generateBoostrapCode(){
    StringBuilder bootstrapCode = new StringBuilder();
    bootstrapCode.append("// Bootstrap code\n");
    bootstrapCode.append("@256\n");
    bootstrapCode.append("D=A\n");
    bootstrapCode.append("@SP\n");
    bootstrapCode.append("M=D\n");
    bootstrapCode.append(functionCall("Sys.init", "0"));
    return bootstrapCode.toString();
  }

  /*
    Write a list of strings to the target file
    Included the expected error handling
  */
  private static void writeLinesToFile(String fileName, List<String> lines){
    try(FileWriter writer = new FileWriter(fileName)){
      for (String line : lines){
        writer.write(line);
      }
    } catch(IOException e){
      System.err.println("Error writing to file: " + e.getMessage());
    }
  }

  /*
    translateVMtoASM method takes a list of strings from the input file
    For each of the command, check if it is an arithmetic command or memory access command
    Write an infinite loop at the end of the file
  */
  private static List<String> translateVMtoASM(List<String> commands, String fileName){
    List<String> translatedCommands = new ArrayList<>();
    for (String command : commands){
      command = command.trim();
      if (command.isEmpty() || command.startsWith("//")) {
        continue;
      }
      String[] parts = command.split("\\s+");
      if (parts.length == 0){
        continue;
      }
      if (isArithmeticCommand(parts[0])){
        translatedCommands.add(translateArithmeticCommand(parts[0]));
      }
      else if (isMemoryAccessCommand(parts[0])){
        translatedCommands.add(translateMemoryAccessCommand(parts, fileName));
      }
      else if (isProgramFlowCommand(parts[0])){
        translatedCommands.add(translateProgramFlowCommand(parts));
      }
      else if (isFunctionCallingCommand(parts[0])){
        translatedCommands.add(translateFunctionCallingCommand(parts));
      }
    }
    // translatedCommands.add("(END_LOOP)\n");
    // translatedCommands.add("@END_LOOP\n");
    // translatedCommands.add("0;JMP");
    return translatedCommands;
  }

  /*
    isArithmeticCommand function check command if it is an arithmetic command
    Input is a string and output is a boolean value
    If the input command is in any of the reserved arithmetic commands, return true
  */
  private static boolean isArithmeticCommand(String command){
    for (String cmd : ARITHMETIC_COMMANDS){
      if (cmd.equals(command)){
        return true;
      }
    }
    return false;
  }

  /*
    Check if a given command is a memory-accessing command
    If the command is in any of the reserved memory accessing command, return true
  */
  private static boolean isMemoryAccessCommand(String command){
    for (String cmd : MEMORY_ACCESS_COMMANDS){
      if (cmd.equals(command)){
        return true;
      }
    }
    return false;
  }

  private static boolean isProgramFlowCommand(String command){
    for (String cmd : PROGRAM_FLOW_COMMANDS){
      if (cmd.equals(command)){
        return true;
      }
    }
    return false;
  }

  private static boolean isFunctionCallingCommand(String command){
    for (String cmd : FUNCTION_CALLING_COMMANDS){
      if (cmd.equals(command)){
        return true;
      }
    }
    return false;
  }

  /*
    Handles the arithmetic command
  */
  private static String translateArithmeticCommand(String command){
    StringBuilder asmCode = new StringBuilder();
    switch(command){
      case "add":
        asmCode.append("// add\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCode.append("M=D+M\n");
        break;
      case "sub":
        asmCode.append("// sub\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCode.append("M=M-D\n");
        break;
      case "neg":
        asmCode.append("// neg\n");
        asmCode.append("@SP\n");
        asmCode.append("A=M-1\n");
        asmCode.append("M=-M\n");
        break;
      case "eq":
        asmCode.append("// eq\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCode.append("D=M-D\n");
        asmCode.append("M=-1\n");
        asmCode.append("@EQUAL").append(labelCounter).append("\n");
        asmCode.append("D;JEQ\n");
        asmCode.append("@SP\n");
        asmCode.append("A=M-1\n");
        asmCode.append("M=0\n");
        asmCode.append("(EQUAL" + labelCounter + ")\n");
        labelCounter++;
        break;
      case "gt":
        asmCode.append("// gt\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCode.append("D=M-D\n");
        asmCode.append("M=-1\n");
        asmCode.append("@GREATER_THAN" + labelCounter + "\n");
        asmCode.append("D;JGT\n");
        asmCode.append("@SP\n");
        asmCode.append("A=M-1\n");
        asmCode.append("M=0\n");
        asmCode.append("(GREATER_THAN" + labelCounter + ")\n");
        labelCounter++;
        break;
      case "lt":
        asmCode.append("// lt\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCode.append("D=M-D\n");
        asmCode.append("M=-1\n");
        asmCode.append("@LESS_THAN" + labelCounter + "\n");
        asmCode.append("D;JLT\n");
        asmCode.append("@SP\n");
        asmCode.append("A=M-1\n");
        asmCode.append("M=0\n");
        asmCode.append("(LESS_THAN" + labelCounter + ")\n");
        labelCounter++;
        break;
      case "and":
        asmCode.append("// and\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCode.append("M=D&M\n");
        break;
      case "or":
        asmCode.append("// or\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCode.append("M=D|M\n");
        break;
      case "not":
        asmCode.append("// not\n");
        asmCode.append("@SP\n");
        asmCode.append("A=M-1\n");
        asmCode.append("M=!M\n");
        break;
      default:
        break;
    }
    return asmCode.toString();
  }

  /*
    A seperate method use to handle push to stack for all the memory accessing method
  */
  private static String pushDToStack(){
    return "@SP\n" + 
            "A=M\n" +
            "M=D\n" +
            "@SP\n" +
            "M=M+1\n";
  }

  /*
    A mapping method used to return the reserved segments
  */
  private static String getSegmentPointer(String segment){
    switch (segment){
      case "local":
        return "LCL";
      case "argument":
        return "ARG";
      case "this":
        return "THIS";
      case "that":
        return "THAT";
      default:
        return "";
    }
  }

  /*
    translateMamoryAccesssCommand helps to handle the memory access commands
    Takes in the command by parts
  */
  private static String translateMemoryAccessCommand(String[] parts, String fileName){
    StringBuilder asmCode = new StringBuilder();
    String segment = parts[1];
    String index = parts[2];
    switch (parts[0]){
      case "push":{
        switch(segment){
          case "constant":
            asmCode.append("// push constant ").append(index).append("\n");
            asmCode.append("@").append(index).append("\n");
            asmCode.append("D=A\n");
            asmCode.append(pushDToStack());
            break;
          case "local":
          case "argument":
          case "this":
          case "that":
            asmCode.append("// push ").append(segment).append(" ").append(index).append("\n");
            asmCode.append("@" + getSegmentPointer(segment) + "\n");
            asmCode.append("D=M\n");
            asmCode.append("@" + index + "\n");
            asmCode.append("A=A+D\n");
            asmCode.append("D=M\n");
            asmCode.append(pushDToStack());
            break;
          case "temp":
            int tempIndex = Integer.parseInt(index);
            asmCode.append("// push temp ").append(tempIndex).append("\n");
            asmCode.append("@5\n");
            asmCode.append("D=A\n");
            asmCode.append("@" + index + "\n");
            asmCode.append("A=A+D\n");
            asmCode.append("D=M\n");
            asmCode.append(pushDToStack());
            break;
          case "static":
            String staticName = parts[0] + "." + index;
            asmCode.append("// push static ").append(index).append("\n");
            asmCode.append("@").append(fileName).append("static").append(index).append("\n");
            asmCode.append("D=M\n");
            asmCode.append(pushDToStack());
            break;
          case "pointer":
            int pointerIndex = Integer.parseInt(index);
            asmCode.append("// push pointer ").append(pointerIndex).append("\n");
            asmCode.append("@" + (pointerIndex == 0 ? "THIS" : "THAT") + "\n");
            asmCode.append("D=M\n");
            asmCode.append(pushDToStack());
            break;
          default:
            break;
        } 
        break;
      }
      case "pop":{
        switch(segment){
          case "local":
          case "argument":
          case "this":
          case "that":
            asmCode.append("// pop ").append(segment).append(" ").append(index).append("\n");
            asmCode.append("@" + getSegmentPointer(segment) + "\n");
            asmCode.append("D=M\n");
            asmCode.append("@").append(index).append("\n");
            asmCode.append("D=D+A\n");
            asmCode.append("@13\n");
            asmCode.append("M=D\n");
            asmCode.append("@SP\n");
            asmCode.append("AM=M-1\n");
            asmCode.append("D=M\n");
            asmCode.append("@13\n");
            asmCode.append("A=M\n");
            asmCode.append("M=D\n");
            break;
          case "temp":
            int tempIndex = Integer.parseInt(index);
            asmCode.append("// pop temp ").append(tempIndex).append("\n");
            asmCode.append("@5\n");
            asmCode.append("D=A\n");
            asmCode.append("@").append(index).append("\n");
            asmCode.append("D=D+A\n");
            asmCode.append("@13\n");
            asmCode.append("M=D\n");
            asmCode.append("@SP\n");
            asmCode.append("AM=M-1\n");
            asmCode.append("D=M\n");
            asmCode.append("@13\n");
            asmCode.append("A=M\n");
            asmCode.append("M=D\n");
            break;
          case "static":
            String staticName = parts[0] + "." + index;
            asmCode.append("// pop static ").append(index).append("\n");
            asmCode.append("@").append(fileName).append(segment).append(index).append("\n");
            asmCode.append("D=A\n");
            asmCode.append("@13\n");
            asmCode.append("M=D\n");
            asmCode.append("@SP\n");
            asmCode.append("AM=M-1\n");
            asmCode.append("D=M\n");
            asmCode.append("@13\n");
            asmCode.append("A=M\n");
            asmCode.append("M=D\n");
            break;
          case "pointer":
            int pointerIndex = Integer.parseInt(index);
            asmCode.append("// pop pointer ").append(pointerIndex).append("\n");
            asmCode.append("@SP\n");
            asmCode.append("AM=M-1\n");
            asmCode.append("D=M\n");
            asmCode.append("@" + (pointerIndex == 0 ? "THIS" : "THAT") + "\n");
            asmCode.append("M=D\n");
            break;
          default:
            break;
        }
        break;
      }
    }
    return asmCode.toString();
  }

  private static String translateProgramFlowCommand(String[] parts){
    StringBuilder asmCode = new StringBuilder();
    switch (parts[0]){
      case "label":
        asmCode.append("(" + parts[1] + ")\n");
        break;
      case "goto":
        asmCode.append("@" + parts[1] + "\n");
        asmCode.append("0;JMP\n");
        break;
      case "if-goto":
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("@" + parts[1] + "\n");
        asmCode.append("D;JNE\n");
        break;
    }
    return asmCode.toString();
  }

  private static String translateFunctionCallingCommand(String[] parts){
    StringBuilder asmCode = new StringBuilder();
    switch (parts[0]){
      case "function":
        if (parts[2].equals("0")){
          asmCode.append("(" + parts[1] + ")\n");
        }
        else{
          return functionInitialization(parts[1], parts[2]);
        }
        break;
      case "call":
        return functionCall(parts[1], parts[2]);
      case "return":
        return functionReturn();
    }
    return asmCode.toString();
  }

  
  private static String functionInitialization(String functionName, String numberOfVariable){
    StringBuilder asmCode = new StringBuilder();
    String label = "Initialize" + functionName + numberOfVariable;
    asmCode.append("(" + functionName + ")\n");
    asmCode.append("\n//Initialize function\n");
    asmCode.append("@" + numberOfVariable + "\n");
    asmCode.append("D=A\n");
    asmCode.append("(" + label + ")\n");
    asmCode.append("@SP\n");
    asmCode.append("A=M\n");
    asmCode.append("M=0\n");
    asmCode.append("@SP\n");
    asmCode.append("M=M+1\n");
    asmCode.append("D=D-1\n");
    asmCode.append("@" + label + "\n");
    asmCode.append("D;JNE\n");
    return asmCode.toString();
  }

  private static String functionCall(String functionName, String numberOfVariable){
    StringBuilder asmCode = new StringBuilder();
    String returnAddress = "RETURN_ADDRESS_" + Integer.toString(returnCounter);
    returnCounter++;
    
    //push return address
    asmCode.append("\n//push return address\n");
    asmCode.append("@" + returnAddress + "\n");
    asmCode.append("D=A\n");
    asmCode.append("@SP\n");
    asmCode.append("A=M\n");
    asmCode.append("M=D\n");
    asmCode.append("@SP\n");
    asmCode.append("M=M+1\n");

    //push LCL, ARG, THIS, THAT
    String[] memorySegmentList = {"LCL", "ARG", "THIS", "THAT"};
    for (String memorySegment : memorySegmentList){
      asmCode.append("\n// push" + memorySegment + "\n");
      asmCode.append("@" + memorySegment + "\n");
      asmCode.append("D=M\n");
      asmCode.append("@SP\n");
      asmCode.append("AM=M+1\n");
      asmCode.append("A=A-1\n");
      asmCode.append("M=D\n");
    }

    //ARG = SP - n - 5
    asmCode.append("\n// ARG = SP - n - 5\n");
    asmCode.append("@SP\n");
    asmCode.append("D=M\n");
    asmCode.append("@5\n");
    asmCode.append("D=D-A\n");
    asmCode.append("@" + numberOfVariable + "\n");
    asmCode.append("D=D-A\n");
    asmCode.append("@ARG\n");
    asmCode.append("M=D\n");

    //LCL = SP
    asmCode.append("\n// LCL = SP\n");
    asmCode.append("@SP\n");
    asmCode.append("D=M\n");
    asmCode.append("@LCL\n");
    asmCode.append("M=D\n");

    //goto f
    asmCode.append("\n// goto f\n");
    asmCode.append("@" + functionName + "\n");
    asmCode.append("0;JMP\n");

    //set return address
    asmCode.append("\n// set return address\n");
    asmCode.append("(" + returnAddress + ")\n");
    //asmCode.append("0;JMP\n");

    return asmCode.toString();
  }

  private static String functionReturn(){
    StringBuilder asmCode = new StringBuilder();
    //FRAME = LCL
    asmCode.append("// FRAME = LCL\n");
    asmCode.append("@LCL\n");
    asmCode.append("D=M\n");
    asmCode.append("@FRAME\n");
    asmCode.append("M=D\n");

    //RET = *(FRAME - 5)
    asmCode.append("\n// RET = *(FRAME - 5)\n");
    asmCode.append("@FRAME\n");
    asmCode.append("D=M\n");
    asmCode.append("@5\n");
    asmCode.append("A=D-A\n");
    asmCode.append("D=M\n");
    asmCode.append("@RET\n");
    asmCode.append("M=D\n");

    //*ARG = pop()
    asmCode.append("\n// *ARG = pop()\n");
    asmCode.append("@SP\n");
    asmCode.append("AM=M-1\n");
    asmCode.append("D=M\n");
    asmCode.append("@ARG\n");
    asmCode.append("A=M\n");
    asmCode.append("M=D\n");

    //SP = ARG + 1
    asmCode.append("\n// SP = ARG + 1\n");
    asmCode.append("@ARG\n");
    asmCode.append("D=M+1\n");
    asmCode.append("@SP\n");
    asmCode.append("M=D\n");

    //THAT = *(FRAME - 1)
    asmCode.append("\n// THAT = *(FRAME - 1)\n");
    asmCode.append("@FRAME\n");
    asmCode.append("A=M-1\n");
    asmCode.append("D=M\n");
    asmCode.append("@THAT\n");
    asmCode.append("M=D\n");

    //THIS = *(FRAME - 2)
    asmCode.append("\n// THAT = *(FRAME - 1)\n");
    asmCode.append("@2\n");
    asmCode.append("D=A\n");
    asmCode.append("@FRAME\n");
    asmCode.append("A=M-D\n");
    asmCode.append("D=M\n");
    asmCode.append("@THIS\n");
    asmCode.append("M=D\n");

    //ARG = *(FRAME - 3)
    asmCode.append("\n// ARG = *(FRAME - 3)\n");
    asmCode.append("@3\n");
    asmCode.append("D=A\n");
    asmCode.append("@FRAME\n");
    asmCode.append("A=M-D\n");
    asmCode.append("D=M\n");
    asmCode.append("@ARG\n");
    asmCode.append("M=D\n");

    //LCL = *(FRAME - 4)
    asmCode.append("\n// LCL = *(FRAME - 4)\n");
    asmCode.append("@4\n");
    asmCode.append("D=A\n");
    asmCode.append("@FRAME\n");
    asmCode.append("A=M-D\n");
    asmCode.append("D=M\n");
    asmCode.append("@LCL\n");
    asmCode.append("M=D\n");

    //goto RET
    asmCode.append("\n// goto RET\n");
    asmCode.append("@RET\n");
    asmCode.append("A=M\n");
    asmCode.append("0;JMP\n");

    return asmCode.toString();
  }

}